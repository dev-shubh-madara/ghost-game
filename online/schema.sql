-- Apply once in the connected Supabase project's SQL editor/migration runner.
-- All mutations go through a narrow authenticated RPC. Never put a service key in the browser.
begin;
create table public.wraith_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
create table public.wraith_friends (
  sender uuid not null references public.wraith_profiles(id) on delete cascade,
  recipient uuid not null references public.wraith_profiles(id) on delete cascade,
  status text not null default 'pending' check(status in ('pending','accepted')),
  created_at timestamptz not null default now(),
  primary key(sender,recipient), check(sender<>recipient)
);
create unique index wraith_friend_pair on public.wraith_friends(least(sender,recipient),greatest(sender,recipient));
create table public.wraith_rooms (
  id uuid primary key default gen_random_uuid(),
  host uuid not null references public.wraith_profiles(id) on delete cascade,
  guest uuid not null references public.wraith_profiles(id) on delete cascade,
  ready boolean not null default false,
  closed boolean not null default false,
  created_at timestamptz not null default now(),
  check(host<>guest)
);
alter table public.wraith_profiles enable row level security;
alter table public.wraith_friends enable row level security;
alter table public.wraith_rooms enable row level security;
revoke all on public.wraith_profiles,public.wraith_friends,public.wraith_rooms from anon,authenticated;
grant select on public.wraith_profiles,public.wraith_friends,public.wraith_rooms to authenticated;
create policy wraith_profile_self on public.wraith_profiles for select to authenticated using(id=auth.uid());
create policy wraith_friend_participants on public.wraith_friends for select to authenticated using(auth.uid() in (sender,recipient));
create policy wraith_room_participants on public.wraith_rooms for select to authenticated using(auth.uid() in (host,guest));
create function public.wraith_action(action text, target uuid default null) returns jsonb
language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); r public.wraith_rooms; n integer;
begin
  if me is null then raise exception 'Log in first'; end if;
  insert into public.wraith_profiles(id) values(me) on conflict do nothing;
  if action='profile' then return jsonb_build_object('id',me);
  elsif action='request' then
    if target=me or target is null then raise exception 'Choose another player ID'; end if;
    if not exists(select 1 from public.wraith_profiles where id=target) then raise exception 'Player ID not found'; end if;
    select count(*) into n from public.wraith_friends where sender=me and created_at>now()-interval '1 hour';
    if n>=20 then raise exception 'Friend request limit reached; try later'; end if;
    insert into public.wraith_friends(sender,recipient) values(me,target) on conflict do nothing;
  elsif action='accept' then
    update public.wraith_friends set status='accepted' where recipient=me and sender=target and status='pending';
    if not found then raise exception 'Incoming request not found'; end if;
  elsif action='decline' then
    delete from public.wraith_friends where recipient=me and sender=target and status='pending';
  elsif action='create' then
    -- Serialize per host so concurrent requests cannot create several active lobbies.
    perform 1 from public.wraith_profiles where id=me for update;
    if not exists(select 1 from public.wraith_friends where status='accepted' and ((sender=me and recipient=target) or (recipient=me and sender=target))) then raise exception 'Accept the friend request first'; end if;
    if exists(select 1 from public.wraith_rooms where not closed and created_at>now()-interval '24 hours' and (host=me or (guest=me and ready))) then raise exception 'Leave your current room first'; end if;
    insert into public.wraith_rooms(host,guest) values(me,target) returning * into r;
    return to_jsonb(r);
  elsif action='join' then
    perform 1 from public.wraith_profiles where id=me for update;
    select * into r from public.wraith_rooms where id=target for update;
    if r.id is null or r.guest<>me or r.closed or r.created_at<now()-interval '24 hours' then raise exception 'Invitation unavailable'; end if;
    if exists(select 1 from public.wraith_rooms where id<>target and not closed and created_at>now()-interval '24 hours' and (host=me or (guest=me and ready))) then raise exception 'Leave your current room first'; end if;
    update public.wraith_rooms set ready=true where id=target returning * into r;
    return to_jsonb(r);
  elsif action='leave' then
    update public.wraith_rooms set closed=true where id=target and me in(host,guest);
  else raise exception 'Unknown action'; end if;
  return jsonb_build_object('ok',true);
end $$;
revoke all on function public.wraith_action(text,uuid) from public,anon;
grant execute on function public.wraith_action(text,uuid) to authenticated;
-- Each member sends on their own channel. A guest cannot impersonate host snapshots.
create function public.wraith_channel_allowed(topic text, writing boolean) returns boolean
language sql stable security definer set search_path='' as $$
 select exists(select 1 from public.wraith_rooms r
 where not r.closed and r.created_at>now()-interval '24 hours'
 and auth.uid() in(r.host,r.guest)
 and (auth.uid()=r.host or r.ready)
 and topic in('wraith:'||r.id::text||':'||r.host::text,'wraith:'||r.id::text||':'||r.guest::text)
 and (not writing or topic='wraith:'||r.id::text||':'||auth.uid()::text));
$$;
revoke all on function public.wraith_channel_allowed(text,boolean) from public,anon;
grant execute on function public.wraith_channel_allowed(text,boolean) to authenticated;
create policy wraith_receive on realtime.messages for select to authenticated
using(extension='broadcast' and public.wraith_channel_allowed((select realtime.topic()),false));
create policy wraith_send on realtime.messages for insert to authenticated
with check(extension='broadcast' and public.wraith_channel_allowed((select realtime.topic()),true));
commit;

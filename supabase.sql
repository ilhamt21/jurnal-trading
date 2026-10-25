-- Jurnal Trading: jalankan sekali di Supabase -> SQL Editor -> New query -> Run

create table if not exists public.trades (
  id text primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  deleted boolean not null default false,
  updated_at timestamptz not null default now()
);

create table if not exists public.accounts (
  id text primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  deleted boolean not null default false,
  updated_at timestamptz not null default now()
);

create index if not exists trades_user_updated on public.trades (user_id, updated_at);
create index if not exists accounts_user_updated on public.accounts (user_id, updated_at);

create or replace function public.jurnal_touch() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trades_touch on public.trades;
create trigger trades_touch before update on public.trades for each row execute function public.jurnal_touch();
drop trigger if exists accounts_touch on public.accounts;
create trigger accounts_touch before update on public.accounts for each row execute function public.jurnal_touch();

alter table public.trades enable row level security;
alter table public.accounts enable row level security;

drop policy if exists "trade milik sendiri" on public.trades;
create policy "trade milik sendiri" on public.trades for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "akun milik sendiri" on public.accounts;
create policy "akun milik sendiri" on public.accounts for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.trades, public.accounts to authenticated;

-- tempat screenshot (privat, tiap pengguna hanya bisa membuka foldernya sendiri)
insert into storage.buckets (id, name, public) values ('shots', 'shots', false)
on conflict (id) do nothing;

drop policy if exists "screenshot baca" on storage.objects;
create policy "screenshot baca" on storage.objects for select to authenticated
  using (bucket_id = 'shots' and (storage.foldername(name))[1] = (select auth.uid())::text);
drop policy if exists "screenshot tambah" on storage.objects;
create policy "screenshot tambah" on storage.objects for insert to authenticated
  with check (bucket_id = 'shots' and (storage.foldername(name))[1] = (select auth.uid())::text);
drop policy if exists "screenshot ubah" on storage.objects;
create policy "screenshot ubah" on storage.objects for update to authenticated
  using (bucket_id = 'shots' and (storage.foldername(name))[1] = (select auth.uid())::text);
drop policy if exists "screenshot hapus" on storage.objects;
create policy "screenshot hapus" on storage.objects for delete to authenticated
  using (bucket_id = 'shots' and (storage.foldername(name))[1] = (select auth.uid())::text);

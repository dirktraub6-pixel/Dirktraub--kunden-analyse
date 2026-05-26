-- Create profiles table linked to auth.users
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- Policy: users can read their own profile
create policy "Users can read their own profile"
  on public.profiles
  for select
  using (auth.uid() = id);

-- Policy: users can update their own profile
create policy "Users can update their own profile"
  on public.profiles
  for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Function to automatically create a profile when a new user signs up
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$;

-- Trigger to call handle_new_user on auth.users insert
create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();

-- Function to automatically update updated_at on profile changes
create or replace function public.handle_updated_at()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Trigger to update updated_at on profile modification
create trigger on_profile_updated
  before update on public.profiles
  for each row
  execute function public.handle_updated_at();

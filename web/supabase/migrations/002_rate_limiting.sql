-- Create rate limiting table for auth actions
create table public.auth_rate_limits (
  id serial primary key,
  identifier text not null,
  action text not null,
  attempted_at timestamptz not null default now()
);

-- Index for efficient lookups by identifier, action, and time window
create index idx_auth_rate_limits_lookup
  on public.auth_rate_limits (identifier, action, attempted_at);

-- Enable Row Level Security (service role only access)
alter table public.auth_rate_limits enable row level security;

-- No RLS policies are created, so only the service role
-- (which bypasses RLS) can read or write to this table.

-- Supabase SQL Editor에서 실행하세요.
create table if not exists transcripts (
    id uuid primary key default gen_random_uuid(),
    source text not null,
    transcript text not null,
    summary text not null,
    created_at timestamptz not null default now()
);

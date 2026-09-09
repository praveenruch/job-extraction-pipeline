create table posting (
	id SERIAL primary key,
	source varchar(255) NOT NULL,
	source_id varchar(255) NOT null,
	raw_html text,
	text text,
	posted_at timestamptz,
	thread_month varchar(7),
	fetched_at timestamptz,

  CONSTRAINT uq_source_id UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS posting_cache (
    id SERIAL primary key,
    thread_id varchar(255) NOT NULL,
    thread_month varchar(7) NOT NULL,
    source varchar(255) NOT NULL,
    postings jsonb NOT NULL,
    fetched_at timestamptz,

  CONSTRAINT uq_thread UNIQUE (source, thread_id)
);

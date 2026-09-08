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
)

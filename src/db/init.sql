create table posting (
	id SERIAL primary key,
	source varchar(255) NOT NULL,
	source_id varchar(255) NOT null,
	raw_html text,
	text text,
	posted_at timestamptz,
	thread_month int4,
	fetched_at timestamptz
)

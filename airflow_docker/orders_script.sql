create table if not exists public.orders(
	order_id varchar not null primary key,
	date date,
	product_name varchar,
	quantity int	
);

select * from public.orders;
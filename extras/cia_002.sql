use cia_002;

-- Master Tables

-- -- Roles Table
create table roles (
	id int auto_increment primary key,
	role_name char(20) not null unique
);

insert into roles (role_name)
values
	("superadmin"),
    ("customer_admin"),
    ("vendor_admin"),
    ("customer"),
    ("vendor");

-- -- Status Table
create table statuses (
	id int auto_increment primary key,
	status_name enum('paid', 'unpaid', 'overdue') not null unique
);

-- Transaction Tables

-- -- Users Table
create table users (
	id int auto_increment primary key,
	username varchar(50) not null unique,
	password_hash varchar(255) not null,
	email varchar(100) not null unique check (email like '%_@__%.__%'),
	phone varchar(15) not null unique check (phone regexp '^[0-9]{10,15}$'),
	first_name varchar(50) not null,
	last_name varchar(50) not null,
	is_active boolean not null default true,
	last_login timestamp null,
	role_id int not null,
	created_by int not null,
	updated_by int not null,
	created_on timestamp default current_timestamp,
	updated_on timestamp default current_timestamp on update current_timestamp,
	foreign key (role_id) references roles(id),
	foreign key (created_by) references users(id),
	foreign key (updated_by) references users(id)
);

-- -- Items Table
create table items (
	id int auto_increment primary key,
	vendor_id int not null,
	description varchar(255) not null unique,
	price decimal(10, 2) not null,
	stock int not null,
	created_by int not null,
	updated_by int not null,
	created_on timestamp default current_timestamp,
	updated_on timestamp default current_timestamp on update current_timestamp,
	foreign key (vendor_id) references users(id),
	foreign key (created_by) references users(id),
	foreign key (updated_by) references users(id)
);

-- -- Invoices Table
create table invoices (
	id int auto_increment primary key,
	customer_id int not null,
	status_id int not null,
	invoice_date date not null,
	total_amount decimal(10, 2) not null,
	created_by int not null,
	updated_by int not null,
	created_on timestamp default current_timestamp,
	updated_on timestamp default current_timestamp on update current_timestamp,
	foreign key (customer_id) references users(id),
	foreign key (status_id) references statuses(id),
	foreign key (created_by) references users(id),
	foreign key (updated_by) references users(id)
);

-- -- Invoice Items Table
create table invoice_items (
	id int auto_increment primary key,
	invoice_id int not null,
	item_id int not null,
	quantity int not null,
	total_price decimal(10, 2) not null,
	created_by int not null,
	updated_by int not null,
	created_on timestamp default current_timestamp,
	updated_on timestamp default current_timestamp on update current_timestamp,
	foreign key (invoice_id) references invoices(id),
	foreign key (item_id) references items(id),
	foreign key (created_by) references users(id),
	foreign key (updated_by) references users(id)
);
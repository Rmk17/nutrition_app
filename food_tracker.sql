create table log_date (
    id integer primary key autoincrement,
    entry_date date not null
);

create table food (
    id integer primary key autoincrement,
    name text not null,
    protein integer not null,
    carbohydrates integer not null,
    fat integer not null,
    calories integer not null
);

create table food_date (
    food_id integer not null,
    log_date_id integer not null,
    primary key(food_id, log_date_id)
);


select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories from food_date 
join log_date on food_date.log_date_id = log_date.id
join food on food.id = food_date.food_id
group by log_date.id
union
select log_date.entry_date, 0, 0, 0, 0 from log_date
where log_date.id not in (select log_date.id from food_date join log_date on
food_date.log_date_id = log_date.id)
order by log_date.entry_date desc
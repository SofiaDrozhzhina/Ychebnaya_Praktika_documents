-- init_db.sql
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    fio VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    teacher VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    id_student INT NOT NULL REFERENCES students(id) ,
    course_id INT NOT NULL REFERENCES courses(id) ,
    date DATE NOT NULL,
    grade VARCHAR(10) -- '5','4','3','2' or 'Не оценено'
);

CREATE TABLE users(

    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    second_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_num VARCHAR(11) NOT NULL,
    national_id VARCHAR(14) NOT NULL,
    age INT NOT NULL
);


CREATE TABLE scores(
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users,
    result INT NOT NULL,
    date DATE NOT NULL,
    Q1 INT NOT NULL,
    Q2 INT NOT NULL,
    Q3 INT NOT NULL,
    Q4 INT NOT NULL,
    Q5 INT NOT NULL,
    Q6 INT NOT NULL,
    Q7 INT NOT NULL,
    Q8 INT NOT NULL,
    Q9 INT NOT NULL
);

INSERT INTO users(name, address, phone_num, national_id) VALUES('محمد صبحي الشحات', 'الزوامل - بلبيس - الشرقية', '01013673244', '29906261301014');
INSERT INTO users(name, address, phone_num, national_id) VALUES('محمد رضا لطفي', 'الزوامل - بلبيس - الشرقية', '01013673244', '29906261301014');
INSERT INTO users(name, address, phone_num, national_id) VALUES('عبد الله محمد خليل', 'الزوامل - بلبيس - الشرقية', '01013673244', '29906261301014');

INSERT INTO scores(user_id, result, date) VALUES('1', '2', '12-6-20');
INSERT INTO scores(user_id, result, date) VALUES('2', '8', '12-4-20');
INSERT INTO scores(user_id, result, date) VALUES('3', '6', '12-3-20');



-- QUESTIONS TABLE 
CREATE TABLE questions(
    id SERIAL PRIMARY KEY,
    question VARCHAR NOT NULL,
    value INT NOT NULL
);


INSERT INTO questions(question, value) VALUES('- ارتفاع درجة الحرارة أكثر من 38', 2);
INSERT INTO questions(question, value) VALUES('- سعال شديد أو متزايد', 2);
INSERT INTO questions(question, value) VALUES('- احتقان شديد بالحلق', 1);
INSERT INTO questions(question, value) VALUES('- قئ أو اسهال', 0);
INSERT INTO questions(question, value) VALUES('- سفر داخل أو خارج مصر: مثال شرم الشيخ/اوروبا', 5);
INSERT INTO questions(question, value) VALUES('- مخالطة لحالة التهاب تنفسي حاد', 4);
INSERT INTO questions(question, value) VALUES('- زيارة مكان صحي ثبت فيه وجود شخص حامل للفيروس', 3);
INSERT INTO questions(question, value) VALUES('- هل أنت أحد العاملين بالقطاع الصحي أو العزل الصحي', 2);
INSERT INTO questions(question, value) VALUES('- تعاني من مرض مزمن: سكر أو ضغط أو قلب أو كلي إلخ', 1);


-- to list all the tables in a database.

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
--create db tables from csv files
CREATE TABLE val_wines_test (name STRING, alcohol FLOAT);
.separator ","
.import wines.csv val_wines_test

--add columns for user liking or disliking drink - default to likes
ALTER TABLE val_wines_test ADD COLUMN likes CHAR(25) DEFAULT 'T' NOT NULL;

--update the likes value of the column to a false (dislike)
UPDATE val_wines_test SET likes = 'F' WHERE name = 'Sweet White'; --pass value as variable

--return random drink with given percentage alcohol from list of liked drinks
SELECT name
FROM val_wines_test --pass this as a variable
WHERE ABS(alcohol - 12.4) = (SELECT MIN(ABS(alcohol - 12.4)) --pass value as a variable
	FROM (
		SELECT *
		FROM val_wines_test
		WHERE likes = 'T'
	)
)
ORDER BY RANDOM() LIMIT 1;
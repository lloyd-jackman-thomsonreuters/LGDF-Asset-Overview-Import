CREATE TABLE names
	(ID INT PRIMARY KEY NOT NULL,
	NAME  CHARACTER(200) NOT NULL,
	TYPE CHARACTER(10) NOT NULL,
	LANGUAGE CHARACTER(3) NOT NULL)

CREATE TABLE xref
	(ID INT PRIMARY KEY NOT NULL,
		CODE CHARACTER(100) NOT NULL,
		TYPE CHARACTER(100) NOT NULL)
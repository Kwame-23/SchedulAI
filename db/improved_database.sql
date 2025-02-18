-- ----------------------------------------------------
-- 1. Create the Database
-- ----------------------------------------------------
CREATE DATABASE IF NOT EXISTS schedulai;
USE schedulai;

-- ----------------------------------------------------
-- 2. Create SessionType Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS SessionType (
    SessionTypeID INT PRIMARY KEY AUTO_INCREMENT,
    SessionTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO SessionType (SessionTypeName)
VALUES
    ('Discussion'),
    ('Independent Study'),
    ('Lab'),
    ('Lecture'),
    ('Period'),
    ('Seminar'),
    ('Set up for grading only')
ON DUPLICATE KEY UPDATE SessionTypeName = SessionTypeName;

-- ----------------------------------------------------
-- 3. Create Room Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Room (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    Location VARCHAR(255) NOT NULL UNIQUE,
    MaxRoomCapacity INT NOT NULL,
    ActiveFlag TINYINT(1) NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1))
) ENGINE=InnoDB;

INSERT INTO Room (Location, MaxRoomCapacity)
VALUES
    ('Apt Hall 216', 74),
    ('Apt Hall 217', 75),
    ('Bio Lab', 33),
    ('D-Lab 102', 58),
    ('Databank Foundation Hall 218', 75),
    ('EE lab', 52),
    ('Fab Lab 103', 31),
    ('Fab Lab 203', 72),
    ('Fab Lab 303', 75),
    ('Jackson Hall 115', 76),
    ('Jackson Hall 116', 79),
    ('Jackson Lab 221', 59),
    ('Jackson Lab 222', 61),
    ('Norton-Motulsky 207A', 58),
    ('Norton-Motulsky 207B', 69),
    ('Nutor Hall 100', 100),
    ('Nutor Hall 115', 73),
    ('Nutor Hall 216', 68),
    ('Radichel MPR', 55),
    ('Science Lab', 47)
ON DUPLICATE KEY UPDATE Location = Location;

-- ----------------------------------------------------
-- 4. Create FacultyType Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS FacultyType (
    FacultyTypeID INT PRIMARY KEY AUTO_INCREMENT,
    FacultyTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO FacultyType (FacultyTypeName)
VALUES
    ('Lecturer'),
    ('Adjunct Faculty'),
    ('Faculty Intern')
ON DUPLICATE KEY UPDATE FacultyTypeName = FacultyTypeName;

-- ----------------------------------------------------
-- 5. Create Lecturer Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Lecturer (
    LecturerID INT PRIMARY KEY AUTO_INCREMENT,
    LecturerName VARCHAR(255) NOT NULL UNIQUE,
    FacultyTypeID INT NOT NULL,
    ActiveFlag TINYINT(1) NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1)),
    FOREIGN KEY (FacultyTypeID) REFERENCES FacultyType(FacultyTypeID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Insert Lecturers without specifying LecturerID
INSERT INTO Lecturer (LecturerName, FacultyTypeID)
VALUES
    ('Acheampong Antwi Afari', 1),
    ('Afiah Agyeman Amponsah-Mensah', 1),
    ('Albert Agyepong', 1),
    ('Albert Cofie', 1),
    ('Alhassan Sullaiman', 1),
    ('Anthony Essel-Anderson', 1),
    ('Anthony Spio', 1),
    ('Awingot Richard Akparibo', 1),
    ('Ayawoa Dagbovie', 1),
    ('Ayorkor Korsah', 1),
    ('Baah Aye Kusi', 1),
    ('Bright Tetteh', 1),
    ('Charles Adjetey', 1),
    ('Christine Onyinah', 1),
    ('David Amatey Sampah', 1),
    ('David Ebo Adjepon-Yamoah', 1),
    ('Dennis Owusu Asamoah', 1),
    ('Dionne Boateng', 1),
    ('Dirk Kleine', 1),
    ('Disraeli Asante-Darko', 1),
    ('Ebenezer Obiri Addo', 1),
    ('Edgar Francis Cooke', 1),
    ('Elena Victoria Rosca', 1),
    ('Enock Opoku', 1),
    ('Enyonam Kudonoo', 1),
    ('Eric Ocran', 1),
    ('George Francois', 1),
    ('Gideon Osabutey', 1),
    ('Godwin Ayetor', 1),
    ('Govindha Ramaiah Yeluripati', 1),
    ('Hassan Wahab', 1),
    ('Hyder Ali Segu Mohamed', 1),
    ('Isaac Nyantakyi', 1),
    ('Ishmael Asiedu', 1),
    ('Jamal-Deen Abdulai', 1),
    ('Joseph Adjei', 1),
    ('Joseph Mensah', 1),
    ('Joseph Oduro-Frimpong', 1),
    ('Josephine Djan', 1),
    ('Justice Kwame Appati', 1),
    ('Kobby Amoah', 1),
    ('Kofi Adu-Labi', 1),
    ('Kwaku Asante', 1),
    ('Kweku Dwomoh', 1),
    ('Maame Mensa-Bonsu', 1),
    ('Maame Yaa Mensa-Bonsu', 1),
    ('Michael Effah Asamoah', 1),
    ('Millicent Awuku', 1),
    ('Miriam Abade-Abugre', 1),
    ('Naa Adjeley Doamekpor', 1),
    ('Nana Kwasi Karikari', 1),
    ('Nathan Nyarko Amanquah', 1),
    ('Nii Tettey', 1),
    ('Patrick Dwomfuor', 1),
    ('Prince Acquaye', 1),
    ('Prince Baah', 1),
    ('Robert Sowah', 1),
    ('Saeed Moomin', 1),
    ('Sampson Dankyi Asare', 1),
    ('Shefi Nelson', 1),
    ('Sihaam Mohammed Sayuti', 1),
    ('Stephen Emmanuel Armah', 1),
    ('Stephen K. Armah', 1),
    ('Sussan Einakian', 1),
    ('Theodora Aryee', 1),
    ('Umut Tosun', 1),
    ('Prince Tetteh', 3),
    ('Emmanuel Darko', 3),
    ('Gabriel Oboamah Affum', 3),
    ('Yayra Azaglo', 3),
    ('Evans Ghansah', 3),
    ('Christelle Afua Asantewaa McCarthy', 3),
    ('Owuraku Obeng Osei-Dwammena', 3),
    ('Akosua Obeng', 3),
    ('Dominic Ayiquaye', 3),
    ('Mary Magdalene Eliason', 3),
    ('Francis Eduku', 1),
    ('Freda Dzradosi', 2),
    ('Jewel Thompson', 1),
    ('Esther Afoley Laryea', 1),
    ('Gordon Kwesi Adomdza', 1),
    ('Keren Arthur', 2),
    ('Samuel Darko', 1),
    ('Joel Bortey', 3),
    ('Kwabena Ampadu Bamfo', 1),
    ('Stephane Nwolley', 2),
    ('Heather Beem', 1),
    ('Adwoa Yirenkyi-Fianko', 2),
    ('Yaw Delali Bensah', 2),
    ('Aminu Shittu', 2),
    ('University of Toronto Faculty', 2),
    ('Annajiat Alim Rasel', 2),
    ('Natalie Fordwor', 2),
    ('Gideon Hosu-Porbley', 2),
    ('Alimsiwen Ayaawan', 1),
    ('Michael Osei', 3),
    ('Brian Botchway', 3),
    ('Katelyn Aba Dadzie', 3),
    ('Noelle Naa Kai Kotei', 3),
    ('Nana Yaa Annorbea Frempong', 3),
    ('Richard Ekumah', 3),
    ('Knowledge Ahadzitse', 3),
    ('Rosemary Abowine', 3),
    ('Elaine Eyram Roberts', 3),
    ('David Asiamah Boateng', 3),
    ('Ewura Abena Asmah', 3),
    ('Karen Effiba Blay', 3),
    ('Emmanuel Affoh', 3),
    ('Benjamin Kofi Ampomah Nkansah', 3),
    ('Nana Adjoa Aseye Senanu', 3),
    ('Anna Naami', 3),
    ('Albert Akatom Bensusan', 1),
    ('Prince Aning', 1),
    ('Rebecca Awuah', 1),
    ('Linda Arthur', 3),
    ('Percy Brown', 3),
    ('Felicity Kuwornoo', 3),
    ('Faith Timoh', 3),
    ('Dickson Akubia', 3),
    ('Nana Banyin Ayeyi Djan', 3),
    ('Nanna Abankwa', 3),
    ('Samantha Mavunga', 3),
    ('Kasim Ibrahim', 3),
    ('Silas Sangmin', 3),
    ('Abdul-Aziz Fuseini', 3),
    ('Elijah Kwaku Adutwum Boateng', 3),
    ('Akwasi Asante-Krobea', 3),
    ('Gideon Donkor Bonsu', 3),
    ('Kweku Yamoah', 3),
    ('Nana Adwoa Newman', 3),
    ('Kwadwo Ansong Annor', 3),
    ('Jesse Korku Seyram Agbenya', 3),
    ('Joseph Kwabena Fosu Okyere', 3),
    ('Nii Aryee Aryeetey', 3),
    ('Shedika Baburononi Hassan', 3),
    ('Dominic Aboagye', 3),
    ('Edith Yaa Okyerewa Boakye', 3),
    ('Emmanuel Annor', 3),
    ('Mariam Korankye', 2),
    ('Eric Acheampong', 2),
    ('Eunice Tachie-Menson', 3),
    ('Edward Laryea', 3),
    ('Klenam Sedegah', 3),
    ('Rahmatu Alhassan Fynn', 3),
    ('Betty Blankson', 3),
    ('Edna Boa Amponsem', 3),
    ('Mahdi Jamaldeen', 3),
    ('Perpetual Asante', 1),
    ('Laila Duwiejua', 1),
    ('David Paapa Asante-Asare', 1),
    ('Richmond Agbelengor', 1),
    ('Joojo Afun', 1),
    ('Acheampong Yaw Amoateng', 1),
    ('Twene Osei', 1),
    ('Anthony Abeo', 1),
    ('Abigail Awuah', 1),
    ('Affum Alhassan', 1),
    ('Aurelia Ayisi', 1),
    ('Danyuo Yiporo', 1),
    ('David Hutchful', 1),
    ('Elizabeth Johnson', 1),
    ('Elsie Aminarh', 1),
    ('Emmanuel Kojo Aidoo', 1),
    ('Emmanuel Obeng Ntow', 1),
    ('Eric Gadzi', 1),
    ('Eugene Daniels', 1),
    ('Iréné Amessouwoe', 1),
    ('Jean Avaala', 1),
    ('Joseph Atatsi', 1),
    ('Jude Samuel Acquaah', 1),
    ('Knowledge Ahadzitse', 3),
    ('Kwaku Yamoah', 1),
    ('Mariam Korankye', 1),
    ('Mensimah Thompson Kwaffo', 1),
    ('Millicent Adjei', 1),
    ('Tatenda Kavu', 1),
    ('William Hoskins', 1),
    ('Yaw Mpeani-Brantuo', 1),
    ('Yvonne Dewortor', 1)
ON DUPLICATE KEY UPDATE LecturerName = LecturerName;

-- ----------------------------------------------------
-- 6. Create Duration Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Duration (
    DurationID INT PRIMARY KEY AUTO_INCREMENT,
    Duration TIME NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO Duration (Duration)
VALUES 
    ('01:00:00'),
    ('01:30:00'),
    ('03:00:00'),
    ('02:00:00'),
    ('01:45:00'),
    ('03:15:00')
ON DUPLICATE KEY UPDATE Duration = Duration;

-- ----------------------------------------------------
-- 7. Create Course Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Course (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL UNIQUE,
    CourseName VARCHAR(255) NOT NULL,
    RequirementType VARCHAR(255) NOT NULL,
    ActiveFlag TINYINT(1) NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1)),
    Credits DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB;

-- Insert Courses without specifying CourseID
INSERT INTO Course (CourseCode, CourseName, RequirementType, Credits)
VALUES
    ('ENGL112', 'Written and Oral Communication', 'Core', 1.0),
    ('ENGL113', 'Text & Meaning', 'Core', 1.0),
    ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Core', 1.0),
    ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Core', 1.0),
    ('ECON101', 'Microeconomics', 'Core', 1.0),
    ('SOAN121', 'Social Theory', 'Core', 1.0),
    ('SOAN111', 'Leadership Seminar 1: What Makes a Good Leader?', 'Core', 0.5),
    ('SOAN211', 'Leadership Seminar 2: Rights, Ethics, and Rule of Law', 'Core', 0.5),
    ('SOAN311', 'Leadership Seminar 3: The Economic Development of a Good Society', 'Core', 0.5),
    ('SOAN411', 'Leadership Seminar 4 for Engineers: Leadership as Service', 'Core', 1.0),
    ('POLS231_202', 'Pan-Africanism', 'Elective', 1.0),
    ('ENG215', 'African Literature', 'Elective', 1.0),
    ('MATH141', 'Calculus 1', 'Core', 1.0),
    ('MATH142', 'Calculus 2', 'Core', 1.0),
    ('MATH152', 'Statistics for Engineering and Economics', 'Core', 1.0),
    ('MATH211', 'Multivariable Calculus and Linear Algebra', 'Core', 1.0),
    ('MATH221', 'Statistics with Probability', 'Core', 1.0),
    ('CS112', 'Computer Programming for Engineering', 'Core', 1.0),
    ('SC112', 'Physics 1', 'Core', 1.0),
    ('SC113', 'Physics 2', 'Core', 1.0),
    ('SC221', 'Materials Science & Chemistry', 'Core', 1.0),
    ('CS222', 'Data Structures and Algorithms', 'Core', 1.0),
    ('CS415', 'Software Engineering', 'Core', 1.0),
    ('CS432', 'Networks and Distributed Computing', 'Core', 1.0),
    ('BUSA304', 'Operations Management', 'Elective', 1.0),
    ('BUSA444', 'Supply Chain Management', 'Elective', 1.0),
    ('CS223', 'Algorithms', 'Core', 1.0),
    ('CS331', 'Computer Architecture', 'Core', 1.0),
    ('CS333', 'Operating Systems', 'Core', 1.0),
    ('CS341', 'Web Development', 'Elective', 1.0),
    ('CS353', 'Artificial Intelligence', 'Elective', 1.0),
    ('BUSA201', 'Financial Accounting', 'Core', 1.0),
    ('BUSA311', 'Managerial Accounting', 'Core', 1.0),
    ('BUSA203', 'Marketing', 'Core', 1.0),
    ('BUSA204', 'Business Strategy', 'Core', 1.0),
    ('EE201', 'Introduction to Electrical Circuits', 'Core', 1.0),
    ('EE301', 'Power Systems', 'Core', 1.0),
    ('ME101', 'Introduction to Mechanics', 'Core', 1.0),
    ('ME201', 'Thermodynamics', 'Core', 1.0),
    ('MIS201', 'Enterprise Systems', 'Core', 1.0),
    ('BUSA341', 'Organizational Behavior', 'Core', 1.0),
    ('BUSA350', 'International Trade & Policy', 'Core', 1.0),
    ('BUSA402', 'Corporate Finance', 'Core', 1.0),
    ('BUSA332', 'Business Law', 'Core', 1.0),
    ('SC231', 'Introduction to Chemistry', 'Core', 1.0),
    ('ENG101', 'English Composition', 'Core', 1.0),
    ('EE451', 'Power Engineering', 'Elective', 1.0),
    ('CS453', 'Robotics', 'Elective', 1.0),
    ('ME411', 'Fluid Mechanics', 'Core', 1.0),
    ('ME431', 'Thermal Systems', 'Core', 1.0),
    ('CS457', 'Data Mining', 'Elective', 1.0),
    ('BUSA462', 'Real Estate Development', 'Elective', 1.0),
    ('SOAN233', 'African Music and Dance', 'Elective', 1.0),
    ('POLS233', 'African Philosophy', 'Elective', 1.0),
    ('ECON102', 'Macroeconomics', 'Core', 1.0),
    ('SOAN229', 'Social Research Methods', 'Core', 1.0),
    ('MATH144', 'Applied Calculus', 'Core', 1.0),
    ('ENGR112', 'Introduction to Engineering', 'Core', 1.0),
    ('ENGR311', 'System Dynamics', 'Core', 1.0),
    ('ENGR312', 'Control Systems', 'Core', 1.0),
    ('ENGR413', 'Project Management', 'Core', 1.0),
    ('CS454', 'Artificial Intelligence', 'Elective', 1.0),
    ('CS424', 'Advanced Database Systems', 'Elective', 1.0),
    ('CS452', 'Computer Graphics', 'Elective', 1.0),
    ('ECON321', 'Risk Management', 'Elective', 1.0),
    ('ECON341', 'Operations Research', 'Elective', 1.0),
    ('BUSA400_A', 'Entrepreneurship I', 'Capstone', 1.0),
    ('BUSA400_B', 'Entrepreneurship II', 'Capstone', 1.0),
    ('CS400_A', 'Thesis I', 'Capstone', 1.0),
    ('CS400_B', 'Thesis II', 'Capstone', 1.0),
    ('BUSA410_A', 'Applied Senior Project', 'Capstone', 1.0),
    ('MIS301', 'E-commerce', 'Core', 1.0),
    ('MIS302', 'Advanced Database Systems', 'Core', 1.0),
    ('MIS303', 'Networks and Distributed Computing', 'Core', 1.0),
    ('MIS304', 'Programming II', 'Core', 1.0),
    ('BUSA442', 'Strategic Brand Management', 'Elective', 1.0),
    ('BUSA423', 'New Product Development', 'Elective', 1.0),
    ('BUSA350', 'International Business', 'Elective', 1.0),
    ('CS313', 'Theory of Computation', 'Core', 1.0),
    ('CS322', 'Data Visualization', 'Elective', 1.0),
    ('CS410', 'Cloud Architecture', 'Elective', 1.0),
    ('CS444', 'Advanced Software Engineering', 'Elective', 1.0),
    ('CS482', 'Natural Language Processing', 'Elective', 1.0),
    ('CS483', 'Computer Vision', 'Elective', 1.0),
    ('ENGR600', 'Advanced Thermodynamics', 'Elective', 1.0),
    ('ME450', 'Sustainable Engineering Design', 'Elective', 1.0),
    ('BUSA500', 'Global Business Strategy', 'Elective', 1.0),
    ('BUSA505', 'Leadership and Ethics', 'Core', 1.0),
    ('EE480', 'Advanced Signal Processing', 'Elective', 1.0),
    ('SC345', 'Quantum Physics', 'Elective', 1.0),
    ('SC350', 'Advanced Material Science', 'Elective', 1.0),
    ('BUSA480', 'Entrepreneurial Finance', 'Elective', 1.0),
    ('BUSA490', 'Digital Marketing', 'Elective', 1.0),
    ('CS474', 'Cybersecurity Management', 'Elective', 1.0),
    ('CS470', 'Quantum Computing', 'Elective', 1.0),
    ('EE460', 'Smart Grid Technologies', 'Elective', 1.0),
    ('EE461', 'Internet of Things (IoT)', 'Elective', 1.0),
    ('MIS300', 'Systems Design and Analysis', 'Core', 1.0),
    ('MIS401', 'Capstone Project in MIS', 'Capstone', 1.0),
    ('MIS402', 'Advanced Business Analytics', 'Elective', 1.0),
    ('BUSA410', 'Global Operations Management', 'Elective', 1.0),
    ('CS411', 'Advanced Programming Paradigms', 'Elective', 1.0),
    ('CS416', 'Machine Learning Operations (MLOps)', 'Elective', 1.0),
    ('CS450', 'Big Data Frameworks', 'Elective', 1.0),
    ('CS460', 'Blockchain and Cryptocurrency', 'Elective', 1.0),
    ('CS465', 'Parallel and Distributed Computing', 'Elective', 1.0),
    ('SC400', 'Capstone Project in Sciences', 'Capstone', 1.0),
    ('ENGR410', 'Robotics Control Systems', 'Elective', 1.0),
    ('ENGR420', 'Autonomous Vehicles', 'Elective', 1.0),
    ('EE490', 'Renewable Energy Systems', 'Elective', 1.0),
    ('EE495', 'Wireless Communication Systems', 'Elective', 1.0),
    ('SC450', 'Advanced Biophysics', 'Elective', 1.0),
    ('SC460', 'Nanotechnology', 'Elective', 1.0),
    ('MATH212', 'Linear Algebra', 'Core', 1.0),
    ('BUSA001', 'Entrepreneurship Universe', 'Core', 1.0),
    ('BUSA132', 'Organizational Behaviour', 'Core', 1.0),
    ('BUSA210', 'Financial Accounting', 'Core', 1.0),
    ('BUSA220', 'Introduction to Finance', 'Core', 1.0),
    ('BUSA224', 'Finance for Non-Finance', 'Core', 1.0),
    ('BUSA321', 'Investments', 'Core', 1.0),
    ('BUSA400_A', 'Thesis 1', 'Core', 1.0),
    ('BUSA402', 'Business Law', 'Core', 1.0),
    ('BUSA405', 'Competitive Strategy', 'Core', 1.0),
    ('BUSA423', 'International Finance', 'Core', 1.0),
    ('BUSA430', 'Human Resource Management', 'Core', 1.0),
    ('BUSA431', 'Real Estate Development', 'Core', 1.0),
    ('BUSA442', 'Strategic Brand Management', 'Elective', 1.0),
    ('BUSA451', 'Development Economics', 'Elective', 1.0),
    ('ECON452', 'Econometrics', 'Elective', 1.0),
    ('ECON455', 'Managerial Economics', 'Elective', 1.0),
    ('ENGR413', 'Project Management & Professional Practice', 'Elective', 1.0),
    ('BUSA424', 'Venture Capital Investment', 'Elective', 1.0),
    ('BUSA432', 'Organization Development', 'Elective', 1.0),
    ('BUSA441', 'Service Marketing', 'Elective', 1.0),
    ('BUSA471', 'Social Enterprise', 'Elective', 1.0),
    ('BUS458', 'Data Analytics for Business', 'Elective', 1.0),
    ('CS213', 'Object-Oriented Programming', 'Core', 1.0),
    ('CS221', 'Discrete Structures and Theory', 'Core', 1.0),
    ('CS361', 'Introduction to Modelling and Simulation', 'Elective', 1.0),
    ('CS442', 'E-Commerce', 'Elective', 1.0),
    ('CS461', 'Data Science', 'Elective', 1.0),
    ('IS333', 'IT Infrastructure and Systems Administration', 'Elective', 1.0),
    ('IS451', 'Information and Systems Security', 'Elective', 1.0),
    ('CS111', 'Introduction to Computing and Information Systems', 'Core', 1.0),
    ('CS212', 'Computer Programming for Computer Science', 'Core', 1.0),
    ('CS323', 'Database Systems', 'Core', 1.0),
    ('CS402', 'CSIS Research Seminar', 'Core', 0.0),
    ('CS434', 'Parallel & Distributed Computing', 'Elective', 1.0),
    ('CS462', 'Cloud Computing', 'Elective', 1.0),
    ('IS371', 'Technology & Ethics', 'Elective', 1.0),
    ('IS361', 'IS Project Management', 'Elective', 1.0),
    ('CS463', 'Computer Game Development', 'Elective', 1.0),
    ('AS111', 'Ashesi Success', 'Core', 0.0),
    ('BUSA400_B', 'Thesis 2', 'Core', 1.0),
    ('MATH121', 'Pre-calculus 1', 'Core', 1.0),
    ('MATH122', 'Pre-calculus 2', 'Core', 1.0),
    ('MATH143', 'Quantitative Methods', 'Core', 1.0),
    ('BUSA220', 'Introduction to Finance', 'Core', 1.0),
    ('SOAN325', 'Research Methods', 'Core', 1.0),
    ('ECON100', 'Principles of Economics', 'Core', 1.0),
    ('CS254', 'Introduction to Artificial Intelligence', 'Core', 1.0),
    ('CS330', 'Hardware and Systems Fundamentals', 'Core', 1.0),
    ('CS432', 'Computer Networks and Data Communications', 'Core', 1.0),
    ('CS410', 'Applied Project', 'Core', 1.0),
    ('MATH161', 'Engineering Calculus', 'Core', 1.0),
    ('MATH251', 'Differential Equations & Numerical Methods', 'Core', 1.0),
    ('EE341', 'AC Electrical Machines', 'Core', 1.0),
    ('EE320', 'Signals & Systems', 'Core', 1.0),
    ('EE321', 'Communication Systems', 'Core', 1.0)
    ('BUSA231', 'Business Communication and Negotiations', 'Core', 1, 1.0),
    ('BUSA400_B', 'Thesis 2', 'Core', 1, 1.0)
ON DUPLICATE KEY UPDATE CourseCode = CourseCode;

-- ----------------------------------------------------
-- 8. Create Cohort Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Cohort (
    CohortID INT PRIMARY KEY AUTO_INCREMENT,
    CohortName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Populate Cohort table with Cohorts A to Z
INSERT INTO Cohort (CohortName)
VALUES
    ('Section A'),
    ('Section B'),
    ('Section C'),
    ('Section D'),
    ('Section E'),
    ('Section F'),
    ('Section G'),
    ('Section H'),
    ('Section I'),
    ('Section J'),
    ('Section K'),
    ('Section L'),
    ('Section M'),
    ('Section N'),
    ('Section O'),
    ('Section P'),
    ('Section Q'),
    ('Section R'),
    ('Section S'),
    ('Section T'),
    ('Section U'),
    ('Section V'),
    ('Section W'),
    ('Section X'),
    ('Section Y'),
    ('Section Z')
ON DUPLICATE KEY UPDATE CohortName = CohortName;

-- ----------------------------------------------------
-- 9. Create Major Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Major (
    MajorID INT PRIMARY KEY AUTO_INCREMENT,
    MajorName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO Major (MajorName)
VALUES
    ('Business Administration'),
    ('Computer Science'),
    ('Management Information Systems (MIS)'),
    ('Computer Engineering'),
    ('Mechatronics Engineering'),
    ('Mechanical Engineering'),
    ('Electrical and Electronic Engineering'),
    ('Law with Public Policy')
ON DUPLICATE KEY UPDATE MajorName = MajorName;

-- ----------------------------------------------------
-- 10. Create Student Table and Populate Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS Student (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    MajorID INT NOT NULL,
    YearNumber INT NOT NULL,
    FOREIGN KEY (MajorID) REFERENCES Major(MajorID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Populate Student table with all possible Major + Year combos
-- (8 majors x 4 years = 32 rows)
INSERT INTO Student (MajorID, YearNumber)
VALUES
    -- Business Administration (MajorID=1), Years 1-4
    (1, 1), (1, 2), (1, 3), (1, 4),
    -- Computer Science (MajorID=2), Years 1-4
    (2, 1), (2, 2), (2, 3), (2, 4),
    -- Management Information Systems (MIS) (MajorID=3), Years 1-4
    (3, 1), (3, 2), (3, 3), (3, 4),
    -- Computer Engineering (MajorID=4), Years 1-4
    (4, 1), (4, 2), (4, 3), (4, 4),
    -- Mechatronics Engineering (MajorID=5), Years 1-4
    (5, 1), (5, 2), (5, 3), (5, 4),
    -- Mechanical Engineering (MajorID=6), Years 1-4
    (6, 1), (6, 2), (6, 3), (6, 4),
    -- Electrical and Electronic Engineering (MajorID=7), Years 1-4
    (7, 1), (7, 2), (7, 3), (7, 4),
    -- Law with Public Policy (MajorID=8), Years 1-4
    (8, 1), (8, 2), (8, 3), (8, 4)
ON DUPLICATE KEY UPDATE MajorID = MajorID, YearNumber = YearNumber;

-- ----------------------------------------------------
-- 11. Create StudentCourseSelection Table
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS StudentCourseSelection (
    SelectionID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,
    CourseCode VARCHAR(20) NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------
-- 12. Create SessionAssignments Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS SessionAssignments (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(255) NOT NULL,
    CohortName VARCHAR(255) NOT NULL,
    SessionType VARCHAR(255) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0,
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (LecturerName) REFERENCES Lecturer(LecturerName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (CohortName) REFERENCES Cohort(CohortName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (SessionType) REFERENCES SessionType(SessionTypeName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------
-- 13. Create SessionSchedule Table and Insert Data
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS SessionSchedule (
    ScheduleID INT PRIMARY KEY AUTO_INCREMENT,
    SessionID INT NOT NULL,
    DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    RoomID INT NOT NULL,
    FOREIGN KEY (SessionID) REFERENCES SessionAssignments(SessionID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------
-- 14. Create UnassignedSessions Table
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS UnassignedSessions (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(255) NOT NULL,
    CohortName VARCHAR(255) NOT NULL,
    SessionType VARCHAR(255) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0,
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (LecturerName) REFERENCES Lecturer(LecturerName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (CohortName) REFERENCES Cohort(CohortName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (SessionType) REFERENCES SessionType(SessionTypeName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

DELIMITER $$

CREATE PROCEDURE sp_upsert_session_with_breaks (
    IN pSessionID   INT,
    IN pDayOfWeek   ENUM('Monday','Tuesday','Wednesday','Thursday','Friday'),
    IN pStartTime   TIME,
    IN pEndTime     TIME,
    IN pRoomID      INT
)
BEGIN
    --------------------------------------------------------------------------
    --  1) Declare all variables and the cursor right after BEGIN
    --------------------------------------------------------------------------
    DECLARE done               INT DEFAULT FALSE;
    DECLARE vScheduleID        INT;
    DECLARE vSessionID         INT;
    DECLARE vOrigDurationSec   INT;
    DECLARE vStart             TIME;
    DECLARE vEnd               TIME;
    DECLARE vPrevEnd           TIME DEFAULT NULL;

    -- Cursor that selects all sessions for (pRoomID, pDayOfWeek) in ascending order
    DECLARE cur CURSOR FOR
        SELECT
            sc.ScheduleID,
            sc.SessionID,
            TIME_TO_SEC(sa.Duration) AS OrigDurationSec,
            sc.StartTime,
            sc.EndTime
        FROM SessionSchedule sc
        JOIN SessionAssignments sa ON sc.SessionID = sa.SessionID
        WHERE sc.RoomID = pRoomID
          AND sc.DayOfWeek = pDayOfWeek
        ORDER BY sc.StartTime;

    -- A continue handler to exit the loop when no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    --------------------------------------------------------------------------
    -- 2) Main logic
    --------------------------------------------------------------------------
    START TRANSACTION;

    -- (A) Upsert the session (insert or update if already exists)
    INSERT INTO SessionSchedule (SessionID, DayOfWeek, StartTime, EndTime, RoomID)
    VALUES (pSessionID, pDayOfWeek, pStartTime, pEndTime, pRoomID)
    ON DUPLICATE KEY UPDATE
        DayOfWeek = VALUES(DayOfWeek),
        StartTime = VALUES(StartTime),
        EndTime   = VALUES(EndTime),
        RoomID    = VALUES(RoomID);

    -- (B) Open the cursor over the final data
    SET vPrevEnd = NULL;
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO vScheduleID, vSessionID, vOrigDurationSec, vStart, vEnd;
        IF done THEN
            LEAVE read_loop;
        END IF;

        IF vPrevEnd IS NOT NULL THEN
            -- If the current StartTime is less than (vPrevEnd + 15 min),
            -- push it forward so there's a 15-min gap
            IF vStart < (vPrevEnd + INTERVAL 15 MINUTE) THEN
                SET vStart = vPrevEnd + INTERVAL 15 MINUTE;
                SET vEnd   = ADDTIME(vStart, SEC_TO_TIME(vOrigDurationSec));

                UPDATE SessionSchedule
                SET StartTime = vStart,
                    EndTime   = vEnd
                WHERE ScheduleID = vScheduleID;
            END IF;
        END IF;

        SET vPrevEnd = vEnd;  -- move forward
    END LOOP;

    CLOSE cur;

    -- (C) Optionally check if the last session extends beyond e.g. 19:00
    -- If yes, you might do ROLLBACK or just proceed.
    -- Example (uncomment if you want to enforce a cutoff):
    -- IF vPrevEnd > '19:00:00' THEN
    --     ROLLBACK;
    --     SIGNAL SQLSTATE '45000'
    --         SET MESSAGE_TEXT = 'Cannot fit sessions before 19:00 cutoff!';
    -- END IF;

    COMMIT;
END $$

DELIMITER ;
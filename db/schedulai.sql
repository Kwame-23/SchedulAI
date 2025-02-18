---------

CREATE DATABASE schedulai;
USE schedulai;

CREATE TABLE SessionType (
    SessionTypeID INT PRIMARY KEY AUTO_INCREMENT,
    SessionTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO SessionType (SessionTypeID, SessionTypeName)
VALUES
(1, 'Discussion'),
(2, 'Independent Study'),
(3, 'Lab'),
(4, 'Lecture'),
(5, 'Period'),
(6, 'Seminar'),
(7, 'Set up for grading only');

CREATE TABLE Room (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    Location VARCHAR(255) NOT NULL UNIQUE,
    MaxRoomCapacity INT NOT NULL
) ENGINE=InnoDB;

INSERT INTO Room (RoomID, Location, MaxRoomCapacity) 
VALUES
(1, 'Apt Hall 216', 74),
(2, 'Apt Hall 217', 75),
(3, 'Bio Lab', 33),
(4, 'D-Lab 102', 58),
(5, 'Databank Foundation Hall 218', 75),
(6, 'EE lab', 52),
(7, 'Fab Lab 103', 31),
(8, 'Fab Lab 203', 72),
(9, 'Fab Lab 303', 75),
(10, 'Jackson Hall 115', 76),
(11, 'Jackson Hall 116', 79),
(12, 'Jackson Lab 221', 59),
(13, 'Jackson Lab 222', 61),
(14, 'Norton-Motulsky 207A', 58),
(15, 'Norton-Motulsky 207B', 69),
(16, 'Nutor Hall 100', 100),
(17, 'Nutor Hall 115', 73),
(18, 'Nutor Hall 216', 68),
(19, 'Radichel MPR', 55),
(20, 'Science Lab', 47);

CREATE TABLE FacultyType (
    FacultyTypeID INT PRIMARY KEY AUTO_INCREMENT,
    FacultyTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO FacultyType (FacultyTypeID, FacultyTypeName)
VALUES
(1, 'Lecturer'),
(2, 'Adjunct Faculty'),
(3, 'Faculty Intern');

CREATE TABLE Lecturer (
    LecturerID INT PRIMARY KEY AUTO_INCREMENT,
    LecturerName VARCHAR(255) NOT NULL,
    FacultyTypeID INT NOT NULL,
    FOREIGN KEY (FacultyTypeID) REFERENCES FacultyType(FacultyTypeID)
) ENGINE=InnoDB;

-- Populate Lecturer table with extracted lecturer names
INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
(1, 'Acheampong Antwi Afari', 1),
(2, 'Afiah Agyeman Amponsah-Mensah', 1),
(3, 'Albert Agyepong', 1),
(4, 'Albert Cofie', 1),
(5, 'Alhassan Sullaiman', 1),
(6, 'Anthony Essel-Anderson', 1),
(7, 'Anthony Spio', 1),
(8, 'Awingot Richard Akparibo', 1),
(9, 'Ayawoa Dagbovie', 1),
(10, 'Ayorkor Korsah', 1),
(11, 'Baah Aye Kusi', 1),
(12, 'Bright Tetteh', 1),
(13, 'Charles Adjetey', 1),
(14, 'Christine Onyinah', 1),
(15, 'David Amatey Sampah', 1),
(16, 'David Ebo Adjepon-Yamoah', 1),
(17, 'Dennis Owusu Asamoah', 1),
(18, 'Dionne Boateng', 1),
(19, 'Dirk Kleine', 1),
(20, 'Disraeli Asante-Darko', 1),
(21, 'Ebenezer Obiri Addo', 1),
(22, 'Edgar Francis Cooke', 1),
(23, 'Elena Victoria Rosca', 1),
(24, 'Enock Opoku', 1),
(25, 'Enyonam Kudonoo', 1),
(26, 'Eric Ocran', 1),
(27, 'George Francois', 1),
(28, 'Gideon Osabutey', 1),
(29, 'Godwin Ayetor', 1),
(30, 'Govindha Ramaiah Yeluripati', 1),
(31, 'Hassan Wahab', 1),
(32, 'Hyder Ali Segu Mohamed', 1),
(33, 'Isaac Nyantakyi', 1),
(34, 'Ishmael Asiedu', 1),
(35, 'Jamal-Deen Abdulai', 1),
(36, 'Joseph Adjei', 1),
(37, 'Joseph Mensah', 1),
(38, 'Joseph Oduro-Frimpong', 1),
(39, 'Josephine Djan', 1),
(40, 'Justice Kwame Appati', 1),
(41, 'Kobby Amoah', 1),
(42, 'Kofi Adu-Labi', 1),
(43, 'Kwaku Asante', 1),
(44, 'Kweku Dwomoh', 1),
(45, 'Maame Mensa-Bonsu', 1),
(46, 'Maame Yaa Mensa-Bonsu', 1),
(47, 'Michael Effah Asamoah', 1),
(48, 'Millicent Awuku', 1),
(49, 'Miriam Abade-Abugre', 1),
(50, 'Naa Adjeley Doamekpor', 1),
(51, 'Nana Kwasi Karikari', 1),
(52, 'Nathan Nyarko Amanquah', 1),
(53, 'Nii Tettey', 1),
(54, 'Patrick Dwomfuor', 1),
(55, 'Prince Acquaye', 1),
(56, 'Prince Baah', 1),
(57, 'Robert Sowah', 1),
(58, 'Saeed Moomin', 1),
(59, 'Sampson Dankyi Asare', 1),
(60, 'Shefi Nelson', 1),
(61, 'Sihaam Mohammed Sayuti', 1),
(62, 'Stephen Emmanuel Armah', 1),
(63, 'Stephen K. Armah', 1),
(64, 'Sussan Einakian', 1),
(65, 'Theodora Aryee', 1),
(66, 'Umut Tosun', 1),
(67, 'Prince Tetteh', 3),
(68, 'Emmanuel Darko', 3),
(69, 'Gabriel Oboamah Affum', 3),
(70, 'Yayra Azaglo', 3),
(71, 'Evans Ghansah', 3),
(72, 'Christelle Afua Asantewaa McCarthy', 3),
(73, 'Owuraku Obeng Osei-Dwammena', 3),
(74, 'Akosua Obeng', 3),
(75, 'Dominic Ayiquaye', 3),
(76, 'Mary Magdalene Eliason', 3),
(77, 'Francis Eduku', 1),
(78, 'Freda Dzradosi', 2),
(79, 'Jewel Thompson', 1),
(80, 'Esther Afoley Laryea', 1),
(81, 'Gordon Kwesi Adomdza', 1),
(82, 'Keren Arthur', 2),
(83, 'Samuel Darko', 1),
(84, 'Joel Bortey', 3),
(85, 'Kwabena Ampadu Bamfo', 1),
(86, 'Stephane Nwolley', 2),
(87, 'Heather Beem', 1),
(88, 'Adwoa Yirenkyi-Fianko', 2),
(89, 'Yaw Delali Bensah', 2),
(90, 'Aminu Shittu', 2),
(91, 'University of Toronto Faculty', 2),
(92, 'Annajiat Alim Rasel', 2),
(93, 'Natalie Fordwor', 2),
(94, 'Gideon Hosu-Porbley', 2),
(95, 'Alimsiwen Ayaawan', 1),
(96, 'Michael Osei', 3),
(97, 'Brian Botchway', 3),
(98, 'Katelyn Aba Dadzie', 3),
(99, 'Noelle Naa Kai Kotei', 3),
(100, 'Nana Yaa Annorbea Frempong', 3),
(101, 'Richard Ekumah', 3),
(102, 'Knowledge Ahadzitse', 3),
(103, 'Rosemary Abowine', 3),
(104, 'Elaine Eyram Roberts', 3),
(105, 'David Asiamah Boateng', 3),
(106, 'Ewura Abena Asmah', 3),
(107, 'Karen Effiba Blay', 3),
(108, 'Emmanuel Affoh', 3),
(109, 'Benjamin Kofi Ampomah Nkansah', 3),
(110, 'Nana Adjoa Aseye Senanu', 3),
(111, 'Anna Naami', 3),
(112, 'Albert Akatom Bensusan', 1),
(113, 'Prince Aning', 1),
(114, 'Rebecca Awuah', 1),
(115, 'Linda Arthur', 3),
(116, 'Percy Brown', 3),
(117, 'Felicity Kuwornoo', 3),
(118, 'Faith Timoh', 3),
(119, 'Dickson Akubia', 3),
(120, 'Nana Banyin Ayeyi Djan', 3),
(121, 'Nanna Abankwa', 3),
(122, 'Samantha Mavunga', 3),
(123, 'Kasim Ibrahim', 3),
(124, 'Silas Sangmin', 3),
(125, 'Abdul-Aziz Fuseini', 3),
(126, 'Elijah Kwaku Adutwum Boateng', 3),
(127, 'Akwasi Asante-Krobea', 3),
(128, 'Gideon Donkor Bonsu', 3),
(129, 'Kweku Yamoah', 3),
(130, 'Nana Adwoa Newman', 3),
(131, 'Kwadwo Ansong Annor', 3),
(132, 'Jesse Korku Seyram Agbenya', 3),
(133, 'Joseph Kwabena Fosu Okyere', 3),
(134, 'Nii Aryee Aryeetey', 3),
(135, 'Shedika Baburononi Hassan', 3),
(136, 'Dominic Aboagye', 3),
(137, 'Edith Yaa Okyerewa Boakye', 3),
(138, 'Emmanuel Annor', 3),
(139, 'Mariam Korankye', 2),
(140, 'Eric Acheampong', 2),
(141, 'Eunice Tachie-Menson', 3),
(142, 'Edward Laryea', 3),
(143, 'Klenam Sedegah', 3),
(144, 'Rahmatu Alhassan Fynn', 3),
(145, 'Betty Blankson', 3),
(146, 'Edna Boa Amponsem', 3),
(147, 'Mahdi Jamaldeen', 3),
(148, 'Perpetual Asante', 1),
(149, 'Laila Duwiejua', 1),
(150, 'David Paapa Asante-Asare', 1),
(151, 'Richmond Agbelengor', 1),
(152, 'Joojo Afun', 1),
(153, 'Acheampong Yaw Amoateng', 1),
(154, 'Twene Osei', 1),
(155, 'Anthony Abeo', 1),
(156, 'Abigail Awuah', 1),
(157, 'Affum Alhassan', 1),
(158, 'Aurelia Ayisi', 1),
(159, 'Danyuo Yiporo', 1),
(160, 'David Hutchful', 1),
(161, 'Elizabeth Johnson', 1),
(162, 'Elsie Aminarh', 1),
(163, 'Emmanuel Kojo Aidoo', 1),
(164, 'Emmanuel Obeng Ntow', 1),
(165, 'Eric Gadzi', 1),
(166, 'Eugene Daniels', 1),
(167, 'Iréné Amessouwoe', 1),
(168, 'Jean Avaala', 1),
(169, 'Joseph Atatsi', 1),
(170, 'Jude Samuel Acquaah', 1),
(171, 'Knowledge Ahadzitse', 3),
(172, 'Kwaku Yamoah', 1),
(173, 'Mariam Korankye', 1),
(174, 'Mensimah Thompson Kwaffo', 1),
(175, 'Millicent Adjei', 1),
(176, 'Tatenda Kavu', 1),
(177, 'William Hoskins', 1),
(178, 'Yaw Mpeani-Brantuo', 1),
(179, 'Yvonne Dewortor', 1);

CREATE TABLE Duration (
    DurationID INT PRIMARY KEY AUTO_INCREMENT,
    Duration TIME NOT NULL
) ENGINE=InnoDB;

INSERT INTO Duration (Duration) 
VALUES 
('01:00:00'),
('01:30:00'),
('03:00:00'),
('02:00:00'),
('01:45:00'),
('03:15:00');

CREATE TABLE Course (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(255) NOT NULL UNIQUE,
    CourseName VARCHAR(255) NOT NULL,
    RequirementType VARCHAR(255) NOT NULL,
    ActiveFlag TINYINT NOT NULL,
    Credits DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(1, 'ENGL112', 'Written and Oral Communication', 'Core', 1, 1.0),
(2, 'ENGL113', 'Text & Meaning', 'Core', 1, 1.0),
(3, 'BUSA161', 'Foundations of Design and Entrepreneurship I', 'Core', 1, 1.0),
(4, 'BUSA162', 'Foundations of Design and Entrepreneurship II', 'Core', 1, 1.0),
(5, 'ECON101', 'Microeconomics', 'Core', 1, 1.0),
(6, 'SOAN121', 'Social Theory', 'Core', 1, 1.0),
(7, 'SOAN111', 'Leadership Seminar 1: What Makes a Good Leader?', 'Core', 1, 0.5),
(8, 'SOAN211', 'Leadership Seminar 2: Rights, Ethics, and Rule of Law', 'Core', 1, 0.5),
(9, 'SOAN311', 'Leadership Seminar 3: The Economic Development of a Good Society', 'Core', 1, 0.5),
(10, 'SOAN411', 'Leadership Seminar 4 for Engineers: Leadership as Service', 'Core', 1, 1.0),
(11, 'POLS231_202', 'Pan-Africanism', 'Elective', 1, 1.0),
(12, 'ENG215', 'African Literature', 'Elective', 1, 1.0),
(13, 'MATH141', 'Calculus 1', 'Core', 1, 1.0),
(14, 'MATH142', 'Calculus 2', 'Core', 1, 1.0),
(15, 'MATH152', 'Statistics for Engineering and Economics', 'Core', 1, 1.0),
(16, 'MATH211', 'Multivariable Calculus and Linear Algebra', 'Core', 1, 1.0),
(17, 'MATH221', 'Statistics with Probability', 'Core', 1, 1.0),
(18, 'CS112', 'Computer Programming for Engineering', 'Core', 1, 1.0),
(19, 'SC112', 'Physics I: Mechanics', 'Core', 1, 1.0),
(20, 'SC113', 'Physics II: Electromagnetism', 'Core', 1, 1.0),
(21, 'SC221', 'Materials Science & Chemistry', 'Core', 1, 1.0),
(22, 'CS222', 'Data Structures and Algorithms', 'Core', 1, 1.0),
(23, 'CS415', 'Software Engineering', 'Core', 1, 1.0),
(24, 'CS432', 'Networks and Distributed Computing', 'Core', 1, 1.0),
(25, 'BUSA304', 'Operations Management', 'Elective', 1, 1.0),
(26, 'BUSA444', 'Supply Chain Management', 'Elective', 1, 1.0),
(27, 'CS223', 'Algorithms', 'Core', 1, 1.0),
(29, 'CS331', 'Computer Architecture', 'Core', 1, 1.0),
(30, 'CS333', 'Operating Systems', 'Core', 1, 1.0),
(31, 'CS341', 'Web Development', 'Elective', 1, 1.0),
(32, 'CS353', 'Artificial Intelligence', 'Elective', 1, 1.0),
(33, 'BUSA201', 'Financial Accounting', 'Core', 1, 1.0),
(34, 'BUSA311', 'Managerial Accounting', 'Core', 1, 1.0),
(35, 'BUSA203', 'Marketing', 'Core', 1, 1.0),
(36, 'BUSA204', 'Business Strategy', 'Core', 1, 1.0),
(37, 'EE201', 'Introduction to Electrical Circuits', 'Core', 1, 1.0),
(38, 'EE301', 'Power Systems', 'Core', 1, 1.0),
(39, 'ME101', 'Introduction to Mechanics', 'Core', 1, 1.0),
(40, 'ME201', 'Thermodynamics', 'Core', 1, 1.0),
(42, 'MIS201', 'Enterprise Systems', 'Core', 1, 1.0),
(43, 'BUSA341', 'Organizational Behavior', 'Core', 1, 1.0),
(45, 'BUSA350', 'International Trade & Policy', 'Core', 1, 1.0),
(46, 'BUSA402', 'Corporate Finance', 'Core', 1, 1.0),
(47, 'BUSA332', 'Business Law', 'Core', 1, 1.0),
(48, 'SC231', 'Introduction to Chemistry', 'Core', 1, 1.0),
(49, 'ENG101', 'English Composition', 'Core', 1, 1.0),
(51, 'EE451', 'Power Engineering', 'Elective', 1, 1.0),
(52, 'CS453', 'Robotics', 'Elective', 1, 1.0),
(53, 'ME411', 'Fluid Mechanics', 'Core', 1, 1.0),
(54, 'ME431', 'Thermal Systems', 'Core', 1, 1.0),
(55, 'CS457', 'Data Mining', 'Elective', 1, 1.0),
(56, 'BUSA462', 'Real Estate Development', 'Elective', 1, 1.0),
(57, 'SOAN233', 'African Music and Dance', 'Elective', 1, 1.0),
(58, 'POLS233', 'African Philosophy', 'Elective', 1, 1.0),
(59, 'ECON102', 'Macroeconomics', 'Core', 1, 1.0),
(60, 'SOAN229', 'Social Research Methods', 'Core', 1, 1.0),
(61, 'MATH144', 'Applied Calculus', 'Core', 1, 1.0),
(62, 'ENGR112', 'Introduction to Engineering', 'Core', 1, 1.0),
(63, 'ENGR311', 'System Dynamics', 'Core', 1, 1.0),
(64, 'ENGR312', 'Control Systems', 'Core', 1, 1.0),
(65, 'ENGR413', 'Project Management', 'Core', 1, 1.0),
(66, 'CS454', 'Artificial Intelligence', 'Elective', 1, 1.0),
(68, 'CS424', 'Advanced Database Systems', 'Elective', 1, 1.0),
(69, 'CS452', 'Computer Graphics', 'Elective', 1, 1.0),
(71, 'ECON321', 'Risk Management', 'Elective', 1, 1.0),
(72, 'ECON341', 'Operations Research', 'Elective', 1, 1.0),
(74, 'BUSA401_A', 'Entrepreneurship I', 'Capstone', 1, 1.0),
(75, 'BUSA401_B', 'Entrepreneurship II', 'Capstone', 1, 1.0),
(76, 'CS400_A', 'Thesis I', 'Capstone', 1, 1.0),
(77, 'CS400_B', 'Thesis II', 'Capstone', 1, 1.0),
(78, 'BUSA410_A', 'Applied Senior Project', 'Capstone', 1, 1.0),
(79, 'MIS301', 'E-commerce', 'Core', 1, 1.0),
(80, 'MIS302', 'Advanced Database Systems', 'Core', 1, 1.0),
(81, 'MIS303', 'Networks and Distributed Computing', 'Core', 1, 1.0),
(82, 'MIS304', 'Programming II', 'Core', 1, 1.0),
(83, 'BUSA442', 'Strategic Brand Management', 'Elective', 1, 1.0),
(84, 'BUSA423', 'New Product Development', 'Elective', 1, 1.0),
(85, 'ENGR300', 'Third Year Group Project & Seminar', 'Core', 1, 0.5),
(86, 'CE122', 'Applied Programming for Engineers', 'Core', 1, 0.5),
(87, 'ENGR212', 'Instrumentation for Engineering', 'Core', 1, 0.5),
(88, 'CE322', 'Digital Systems Design', 'Core', 1, 1.0),
(89, 'CE451', 'Embedded Systems', 'Core', 1, 1.0),
(90, 'CS313', 'Intermediate Computer Programming', 'Core', 1, 1.0),
(92, 'CS433', 'Operating Systems and Systems Administration', 'Core', 1, 1.0),
(93, 'CS456', 'Algorithm Design & Analysis', 'Core', 1, 1.0),
(94, 'ME311', 'Mechanics of Materials/Structural Engineering', 'Core', 1, 1.0),
(95, 'ME301', 'Mechanical Machine Design', 'Core', 1, 1.0),
(97, 'ME421', 'Thermal Systems and Applications', 'Core', 1, 1.0),
(99, 'EE222', 'Circuits and Electronics', 'Core', 1, 1.0),
(100, 'EE242', 'Introduction to Electrical Machines and Power Electronics', 'Core', 1, 1.0),
(101, 'EE342', 'Advanced Electrical Machines and Power Electronics', 'Core', 1, 1.0),
(102, 'EE453', 'Power Systems Analysis', 'Elective', 1, 1.0),
(104, 'CS412', 'Concepts of Programming Languages', 'Elective', 1, 1.0),
(106, 'CS443', 'Mobile App Development', 'Elective', 1, 1.0),
(108, 'CS455', 'Applied Cryptography and Security', 'Elective', 1, 1.0),
(110, 'CS413', 'Human-Computer Interaction', 'Elective', 1, 1.0),
(111, 'ENGR400', 'Senior Project', 'Capstone', 1, 1.0),
(112, 'ENGR401', 'Senior Project and Seminar', 'Capstone', 1, 1.0),
(113, 'ENGR414', 'Environmental Science and Engineering', 'Elective', 1, 1.0),
(114, 'SC141', 'Introduction to Biology', 'Core', 1, 1.0),
(115, 'SC241', 'Biochemistry', 'Core', 1, 1.0),
(116, 'SC341', 'Molecular Biology', 'Core', 1, 1.0),
(118, 'ENGR313', 'Project Management', 'Core', 1, 1.0),
(119, 'EE421', 'Digital and Analog Signal Processing', 'Elective', 1, 1.0),
(120, 'CS451', 'VLSI: Embedded Systems', 'Elective', 1, 1.0),
(121, 'CS311', 'Theory of Computation', 'Core', 1, 1.0),
(122, 'MIS101', 'Introduction to Information Systems', 'Core', 1, 1.0),
(123, 'MIS401', 'Thesis in MIS', 'Capstone', 1, 1.0),
(124, 'MIS402', 'Thesis II in MIS', 'Capstone', 1, 1.0),
(125, 'CS417', 'Computational Theory', 'Core', 1, 1.0),
(126, 'CS425', 'Distributed Systems', 'Elective', 1, 1.0),
(127, 'CS435', 'Cloud Computing', 'Elective', 1, 1.0),
(128, 'CS458', 'Machine Learning', 'Elective', 1, 1.0),
(129, 'CS459', 'Deep Learning', 'Elective', 1, 1.0),
(130, 'CS314', 'Human-Computer Interaction', 'Core', 1, 1.0),
(133, 'SC112', 'Physics 1', 'Core', 1, 1.0),
(134, 'SC113', 'Physics 2', 'Core', 1, 1.0),
(135, 'CS121', 'Introduction to Programming', 'Core', 1, 1.0),
(136, 'CS211', 'Data Analytics', 'Elective', 1, 1.0),
(137, 'CS441', 'Information Security', 'Elective', 1, 1.0),
(138, 'BUSA401_C', 'Leadership for Entrepreneurs', 'Capstone', 1, 1.0),
(139, 'ENG101', 'Introduction to Technical Writing', 'Core', 1, 1.0),
(140, 'CS200', 'Game Design', 'Elective', 1, 1.0),
(141, 'CS401', 'Mobile Computing', 'Elective', 1, 1.0),
(142, 'CS404', 'Big Data Analytics', 'Elective', 1, 1.0),
(143, 'CS440', 'Blockchain Technologies', 'Elective', 1, 1.0),
(144, 'CS442', 'Advanced Networking', 'Elective', 1, 1.0),
(145, 'ENG200', 'Engineering Ethics', 'Core', 1, 1.0),
(146, 'EE311', 'Communication Systems', 'Core', 1, 1.0),
(147, 'BUSA100', 'Business Fundamentals', 'Core', 1, 1.0),
(148, 'BUSA101', 'Introduction to Accounting', 'Core', 1, 1.0),
(149, 'CS456', 'Algorithm Design', 'Core', 1, 1.0),
(150, 'CS461', 'Digital Forensics', 'Elective', 1, 1.0),
(151, 'ENGR500', 'Advanced Control Systems', 'Core', 1, 1.0),
(152, 'ENGR501', 'Microcontroller Programming', 'Elective', 1, 1.0),
(153, 'ENGR502', 'Advanced Robotics', 'Elective', 1, 1.0),
(154, 'CS320', 'Data Visualization', 'Elective', 1, 1.0),
(155, 'CS480', 'Capstone Project', 'Capstone', 1, 1.0),
(156, 'MIS210', 'Business Intelligence', 'Core', 1, 1.0),
(157, 'MIS411', 'Information Systems Auditing', 'Elective', 1, 1.0),
(158, 'EE310', 'Power Electronics', 'Core', 1, 1.0),
(159, 'EE450', 'Electromagnetic Field Theory', 'Core', 1, 1.0),
(160, 'EE499', 'Capstone Project in Electrical Engineering', 'Capstone', 1, 1.0),
(161, 'ME340', 'Heat and Mass Transfer', 'Core', 1, 1.0),
(162, 'ME442', 'Computer Aided Design (CAD) / Manufacturing (CAM)', 'Elective', 1, 1.0),
(163, 'BUSA370', 'Innovation and Design Thinking', 'Elective', 1, 1.0),
(164, 'BUSA460', 'International Business', 'Elective', 1, 1.0),
(165, 'SOAN230', 'Cultural Anthropology', 'Elective', 1, 1.0),
(166, 'POLS340', 'International Relations', 'Elective', 1, 1.0),
(167, 'ENG202', 'Scientific Writing', 'Core', 1, 1.0),
(168, 'CS410', 'Cloud Architecture', 'Elective', 1, 1.0),
(169, 'CS444', 'Advanced Software Engineering', 'Elective', 1, 1.0),
(170, 'CS482', 'Natural Language Processing', 'Elective', 1, 1.0),
(171, 'CS483', 'Computer Vision', 'Elective', 1, 1.0),
(172, 'ENGR600', 'Advanced Thermodynamics', 'Elective', 1, 1.0),
(173, 'ME450', 'Sustainable Engineering Design', 'Elective', 1, 1.0),
(174, 'BUSA500', 'Global Business Strategy', 'Elective', 1, 1.0),
(175, 'BUSA505', 'Leadership and Ethics', 'Core', 1, 1.0),
(176, 'EE480', 'Advanced Signal Processing', 'Elective', 1, 1.0),
(177, 'SC345', 'Quantum Physics', 'Elective', 1, 1.0),
(178, 'SC350', 'Advanced Material Science', 'Elective', 1, 1.0),
(179, 'BUSA480', 'Entrepreneurial Finance', 'Elective', 1, 1.0),
(180, 'BUSA490', 'Digital Marketing', 'Elective', 1, 1.0),
(181, 'CS474', 'Cybersecurity Management', 'Elective', 1, 1.0),
(182, 'CS470', 'Quantum Computing', 'Elective', 1, 1.0),
(183, 'EE460', 'Smart Grid Technologies', 'Elective', 1, 1.0),
(184, 'EE461', 'Internet of Things (IoT)', 'Elective', 1, 1.0),
(185, 'MIS300', 'Systems Design and Analysis', 'Core', 1, 1.0),
(186, 'MIS401', 'Capstone Project in MIS', 'Capstone', 1, 1.0),
(187, 'MIS402', 'Advanced Business Analytics', 'Elective', 1, 1.0),
(188, 'BUSA410', 'Global Operations Management', 'Elective', 1, 1.0),
(189, 'CS411', 'Advanced Programming Paradigms', 'Elective', 1, 1.0),
(190, 'CS416', 'Machine Learning Operations (MLOps)', 'Elective', 1, 1.0),
(191, 'CS450', 'Big Data Frameworks', 'Elective', 1, 1.0),
(192, 'CS460', 'Blockchain and Cryptocurrency', 'Elective', 1, 1.0),
(193, 'CS465', 'Parallel and Distributed Computing', 'Elective', 1, 1.0),
(194, 'SC400', 'Capstone Project in Sciences', 'Capstone', 1, 1.0),
(195, 'ENGR410', 'Robotics Control Systems', 'Elective', 1, 1.0),
(196, 'ENGR420', 'Autonomous Vehicles', 'Elective', 1, 1.0),
(197, 'EE490', 'Renewable Energy Systems', 'Elective', 1, 1.0),
(198, 'EE495', 'Wireless Communication Systems', 'Elective', 1, 1.0),
(199, 'SC450', 'Advanced Biophysics', 'Elective', 1, 1.0),
(200, 'SC460', 'Nanotechnology', 'Elective', 1, 1.0),
(201, 'MATH212', 'Linear Algebra', 'Core', 1, 1.0),
(202, 'BUSA001', 'Entrepreneurship Universe', 'Core', 1, 1.0),
(203, 'BUSA132', 'Organizational Behaviour', 'Core', 1, 1.0),
(204, 'BUSA210', 'Financial Accounting', 'Core', 1, 1.0),
(205, 'BUSA220', 'Introduction to Finance', 'Core', 1, 1.0),
(206, 'BUSA224', 'Finance for Non-Finance', 'Core', 1, 1.0),
(207, 'BUSA321', 'Investments', 'Core', 1, 1.0),
(208, 'BUSA400_A', 'Thesis 1', 'Core', 1, 1.0),
(209, 'BUSA402', 'Business Law', 'Core', 1, 1.0),
(210, 'BUSA405', 'Competitive Strategy', 'Core', 1, 1.0),
(211, 'BUSA423', 'International Finance', 'Core', 1, 1.0),
(212, 'BUSA430', 'Human Resource Management', 'Core', 1, 1.0),
(213, 'BUSA431', 'Real Estate Development', 'Core', 1, 1.0),
(214, 'BUSA442', 'Strategic Brand Management', 'Elective', 1, 1.0),
(215, 'BUSA451', 'Development Economics', 'Elective', 1, 1.0),
(216, 'ECON452', 'Econometrics', 'Elective', 1, 1.0),
(217, 'ECON455', 'Managerial Economics', 'Elective', 1, 1.0),
(218, 'ENGR413', 'Project Management & Professional Practice', 'Elective', 1, 1.0),
(219, 'BUSA424', 'Venture Capital Investment', 'Elective', 1, 1.0),
(220, 'BUSA432', 'Organization Development', 'Elective', 1, 1.0),
(221, 'BUSA441', 'Service Marketing', 'Elective', 1, 1.0),
(222, 'BUSA471', 'Social Enterprise', 'Elective', 1, 1.0),
(223, 'BUS458', 'Data Analytics for Business', 'Elective', 1, 1.0),
(224, 'CS213', 'Object-Oriented Programming', 'Core', 1, 1.0),
(225, 'CS221', 'Discrete Structures and Theory', 'Core', 1, 1.0),
(226, 'CS361', 'Introduction to Modelling and Simulation', 'Elective', 1, 1.0),
(227, 'CS442', 'E-Commerce', 'Elective', 1, 1.0),
(228, 'CS461', 'Data Science', 'Elective', 1, 1.0),
(229, 'IS333', 'IT Infrastructure and Systems Administration', 'Elective', 1, 1.0),
(230, 'IS451', 'Information and Systems Security', 'Elective', 1, 1.0),
(231, 'CS111', 'Introduction to Computing and Information Systems', 'Core', 1, 1.0),
(232, 'CS212', 'Computer Programming for Computer Science', 'Core', 1, 1.0),
(233, 'CS323', 'Database Systems', 'Core', 1, 1.0),
(234, 'CS402', 'CSIS Research Seminar', 'Core', 1, 0.0),
(235, 'CS434', 'Parallel & Distributed Computing', 'Elective', 1, 1.0),
(236, 'CS462', 'Cloud Computing', 'Elective', 1, 1.0),
(237, 'IS371', 'Technology & Ethics', 'Elective', 1, 1.0),
(238, 'IS361', 'IS Project Management', 'Elective', 1, 1.0),
(239, 'CS463', 'Computer Game Development', 'Elective', 1, 1.0),
(240, 'AS111', 'Ashesi Success', 'Core', 1, 0.0),
(241, 'BUSA400_B', 'Thesis 2', 'Core', 1, 1.0),
(78, 'BUSA410_B', 'Applied Senior Project', 'Capstone', 1, 1.0),
(242, 'MATH121', 'Pre-calculus 1', 'Core', 1, 1.0),
(243, 'MATH122', 'Pre-calculus 2', 'Core', 1, 1.0),
(244, 'MATH143', 'Quantitative Methods', 'Core', 1, 1.0),
(245, 'BUSA220', 'Introduction to Finance', 'Core', 1, 1.0),
(246, 'SOAN325', 'Research Methods', 'Core', 1, 1.0),
(247, 'ECON100', 'Principles of Economics', 'Core', 1, 1.0),
(248, 'CS254', 'Introduction to Artificial Intelligence', 'Core', 1, 1.0),
(249, 'CS330', 'Hardware and Systems Fundamentals', 'Core', 1, 1.0),
(250, 'CS432', 'Computer Networks and Data Communications', 'Core', 1, 1.0),
(251, 'CS410', 'Applied Project', 'Core', 1, 1.0),
(252, 'MATH161', 'Engineering Calculus', 'Core', 1, 1.0),
(253, 'MATH251', 'Differential Equations & Numerical Methods', 'Core', 1, 1.0),
(254, 'EE341', 'AC Electrical Machines', 'Core', 1, 1.0),
(255, 'EE320', 'Signals & Systems', 'Core', 1, 1.0),
(256, 'EE321', 'Communication Systems', 'Core', 1, 1.0),
(257, 'ME441', 'Manufacturing Processes', 'Core', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(258, 'BUSA231', 'Business Communication and Negotiations', 'Core', 1, 1.0),
(259, 'BUSA400_B', 'Thesis 2', 'Core', 1, 1.0);

INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('ELECTIVE1', 'Elective (4 credits)', 'Elective', 1, 1.0);

INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('ELECTIVE2', 'Extra Major Elective', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(290, 'SOAN301', 'Introduction to Africana Studies: The Global Black Experience', 'Elective', 1, 1.0);



CREATE TABLE Cohort (
    CohortID INT PRIMARY KEY AUTO_INCREMENT,
    CohortName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Populate Cohort table with Cohorts A to Z
INSERT INTO Cohort (CohortID, CohortName)
VALUES
(1, 'Section A'),
(2, 'Section B'),
(3, 'Section C'),
(4, 'Section D'),
(5, 'Section E'),
(6, 'Section F'),
(7, 'Section G'),
(8, 'Section H'),
(9, 'Section I'),
(10, 'Section J'),
(11, 'Section K'),
(12, 'Section L'),
(13, 'Section M'),
(14, 'Section N'),
(15, 'Section O'),
(16, 'Section P'),
(17, 'Section Q'),
(18, 'Section R'),
(19, 'Section S'),
(20, 'Section T'),
(21, 'Section U'),
(22, 'Section V'),
(23, 'Section W'),
(24, 'Section X'),
(25, 'Section Y'),
(26, 'Section Z');


CREATE TABLE SessionAssignments (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(100) NOT NULL,
    CohortName VARCHAR(50) NOT NULL,
    SessionType VARCHAR(50) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;



CREATE TABLE SessionSchedule (
    ScheduleID INT PRIMARY KEY AUTO_INCREMENT,
    SessionID INT NOT NULL,
    DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    RoomID INT NOT NULL,
    FOREIGN KEY (SessionID) REFERENCES SessionAssignments(SessionID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
) ENGINE=InnoDB;

CREATE TABLE Major (
    MajorID INT PRIMARY KEY AUTO_INCREMENT,
    MajorName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO Major (MajorID, MajorName)
VALUES
(1, 'Business Administration'),
(2, 'Computer Science'),
(3, 'Management Information Systems (MIS)'),
(4, 'Computer Engineering'),
(5, 'Mechatronics Engineering'),
(6, 'Mechanical Engineering'),
(7, 'Electrical and Electronic Engineering'),
(8, 'Law with Public Policy');

ALTER TABLE Lecturer ADD COLUMN ActiveFlag INTEGER NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1));
ALTER TABLE Room ADD COLUMN ActiveFlag INTEGER NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1));

ALTER TABLE SessionAssignments
ADD COLUMN NumberOfEnrollments INT NOT NULL DEFAULT 0;

ALTER TABLE SessionSchedule
ADD COLUMN RoomName VARCHAR(255) NOT NULL;


ALTER TABLE SessionSchedule
DROP FOREIGN KEY sessionschedule_ibfk_2;
ALTER TABLE SessionSchedule
DROP COLUMN RoomID;

UPDATE Room
SET ActiveFlag = 1;

-- -----------------------------------------
-- 1. Create the Student table
-- -----------------------------------------
CREATE TABLE Student (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    MajorID INT NOT NULL,
    YearNumber INT NOT NULL,
    FOREIGN KEY (MajorID) REFERENCES Major(MajorID)
) ENGINE=InnoDB;

-- -----------------------------------------
-- 2. Populate Student table with all
--    possible Major + Year combos
--    (8 majors x 4 years = 32 rows)
-- -----------------------------------------
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
    (8, 1), (8, 2), (8, 3), (8, 4);

CREATE TABLE StudentCourseSelection (
    SelectionID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,
    CourseCode VARCHAR(255) NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
) ENGINE=InnoDB;

ALTER TABLE StudentCourseSelection
ADD COLUMN Type ENUM(
    'No Subtype', 
    'Type I', 'Type II', 'Type III', 'Type IV', 'Type V', 
    'Type VI', 'Type VII', 'Type VIII', 'Type IX', 'Type X'
) NOT NULL DEFAULT 'No Subtype';

CREATE TABLE UnassignedSessions (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(100) NOT NULL,
    CohortName VARCHAR(50) NOT NULL,
    SessionType VARCHAR(50) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

--
-- 1) Create the ProgramPlan table
--
CREATE TABLE ProgramPlan (
    ProgramPlanID INT PRIMARY KEY AUTO_INCREMENT,
    MajorID INT NOT NULL,
    YearNumber INT NOT NULL,
    SemesterNumber INT NOT NULL,
    SubType VARCHAR(50) NULL,  -- "I", "II", "III", or NULL
    CourseCode VARCHAR(255) NOT NULL,

    FOREIGN KEY (MajorID) REFERENCES Major(MajorID),
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
) ENGINE=InnoDB;


-- Add Program Plans for Electrical and Electronic Engineering (MajorID=7)

-- Year 1, Semester 1
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 1, 1, '', 'AS111'),
    (7, 1, 1, '', 'ENGL112'),
    (7, 1, 1, '', 'BUSA161'),
    (7, 1, 1, '', 'ENGR112'),
    (7, 1, 1, '', 'MATH161');

-- Year 1, Semester 2
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 1, 2, '', 'CS112'),
    (7, 1, 2, '', 'MATH211'),
    (7, 1, 2, '', 'BUSA162'),
    (7, 1, 2, '', 'ME101'),
    (7, 1, 2, '', 'SOAN111');

-- Year 2, Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 2, 3, '', 'SC113'),
    (7, 2, 3, '', 'ME201'),
    (7, 2, 3, '', 'MATH152'),
    (7, 2, 3, '', 'SOAN211'),
    (7, 2, 3, '', 'ME442');

-- Year 2, Semester 4
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 2, 4, '', 'MATH251'),
    (7, 2, 4, '', 'SOAN311'),
    (7, 2, 4, '', 'EE222'),
    (7, 2, 4, '', 'SC221'),
    (7, 2, 4, '', 'ENGL113'),
    (7, 2, 4, '', 'CE122');

-- Year 3, Semester 5
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 3, 5, '', 'EE341'),
    (7, 3, 5, '', 'ENGR311'),
    (7, 3, 5, '', 'SOAN411'),
    (7, 3, 5, '', 'ENGR212'),
    (7, 3, 5, '', 'ENGR300'),
    (7, 3, 5, '', 'EE320');

-- Year 3, Semester 6
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 3, 6, '', 'ENGR312'),
    (7, 3, 6, '', 'EE342'),
    (7, 3, 6, '', 'CE322'),
    (7, 3, 6, '', 'EE321'),
    (7, 3, 6, '', 'ELECTIVE1');

-- Year 4, Semester 7
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 4, 7, '', 'EE451'),
    (7, 4, 7, '', 'ELECTIVE1'),
    (7, 4, 7, '', 'ECON100'),
    (7, 4, 7, '', 'CE451'),
    (7, 4, 7, '', 'ELECTIVE2');

-- Year 4, Semester 8
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 4, 8, '', 'ENGR413'),
    (7, 4, 8, '', 'ELECTIVE1'),
    (7, 4, 8, '', 'ELECTIVE2'),
    (7, 4, 8, '', 'ENGR401');


--- BUSINESS ADMINISTRATION

-- Year 1, Semester 1 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 1, 'I', 'AS111'),    -- Ashesi Success
(1, 1, 1, 'I', 'MATH121'),  -- Pre-calculus 1
(1, 1, 1, 'I', 'ENGL112'),  -- Written and Oral Communication
(1, 1, 1, 'I', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
(1, 1, 1, 'I', 'CS111');    -- Introduction to Computing and Information Systems

-- Year 1, Semester 1 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 1, 'II', 'AS111'),
(1, 1, 1, 'II', 'MATH141'),
(1, 1, 1, 'II', 'ENGL112'),
(1, 1, 1, 'II', 'BUSA161'),
(1, 1, 1, 'II', 'CS111');

-- Year 1, Semester 2 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 2, 'I', 'SOAN111'),
(1, 1, 2, 'I', 'MATH122'),
(1, 1, 2, 'I', 'ENGL113'),
(1, 1, 2, 'I', 'BUSA162');

-- Year 1, Semester 2 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 2, 'II', 'SOAN111'),
(1, 1, 2, 'II', 'MATH142'),
(1, 1, 2, 'II', 'ENGL113'),
(1, 1, 2, 'II', 'BUSA162');

-- Year 2, Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 2, 3, '', 'SOAN211'),
(1, 2, 3, '', 'MATH221'),
(1, 2, 3, '', 'ECON101'),
(1, 2, 3, '', 'BUSA210'),
(1, 2, 3, '', 'ELECTIVE1');

-- Year 2, Semester 4
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 2, 4, '', 'SOAN311'),
(1, 2, 4, '', 'MATH143'),
(1, 2, 4, '', 'ECON102'),
(1, 2, 4, '', 'BUSA220'),
(1, 2, 4, '', 'BUSA132');

-- Year 3, Semester 5
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 3, 5, '', 'BUSA304'),
(1, 3, 5, '', 'BUSA350'),
(1, 3, 5, '', 'SOAN411'),
(1, 3, 5, '', 'BUSA203'),
(1, 3, 5, '', 'BUSA422');

-- Year 3, Semester 6
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 3, 6, '', 'SOAN325'),
(1, 3, 6, '', 'BUSA311'),
(1, 3, 6, '', 'SOAN411'),
(1, 3, 6, '', 'BUSA402'),
(1, 3, 6, '', 'ELECTIVE1');

-- Year 4, Semester 7 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'I', 'BUSA405'),
(1, 4, 7, 'I', 'ELECTIVE1'),
(1, 4, 7, 'I', 'BUSA321'),
(1, 4, 7, 'I', 'BUSA400_A');

-- Year 4, Semester 7 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'II', 'BUSA405'),
(1, 4, 7, 'II', 'ELECTIVE1'),
(1, 4, 7, 'II', 'BUSA321'),
(1, 4, 7, 'II', 'BUSA410_A');

-- Year 4, Semester 7 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'III', 'BUSA405'),
(1, 4, 7, 'III', 'ELECTIVE1'),
(1, 4, 7, 'III', 'BUSA321'),
(1, 4, 7, 'III', 'BUSA401_A');

-- Year 4, Semester 8 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'I', 'BUSA231'),
(1, 4, 8, 'I', 'ELECTIVE1'),
(1, 4, 8, 'I', 'ELECTIVE1'),
(1, 4, 8, 'I', 'BUSA400_B');

-- Year 4, Semester 8 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'II', 'BUSA231'),
(1, 4, 8, 'II', 'ELECTIVE1'),
(1, 4, 8, 'II', 'ELECTIVE1'),
(1, 4, 8, 'II', 'BUSA410_B');

-- Year 4, Semester 8 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'III', 'BUSA231'),
(1, 4, 8, 'III', 'ELECTIVE1'),
(1, 4, 8, 'III', 'ELECTIVE1'),
(1, 4, 8, 'III', 'BUSA401_B');

-- ----------------------------------------------------
-- Insert Correct ProgramPlan Entries for Computer Science (MajorID = 2)
-- ----------------------------------------------------

-- Year 1
-- Semester 1
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 1, 'I', 'AS111'),       -- Ashesi Success
    (2, 1, 1, 'I', 'MATH121'),     -- Pre-calculus 1
    (2, 1, 1, 'I', 'ENGL112'),     -- Written and Oral Communication
    (2, 1, 1, 'I', 'BUSA161'),     -- Foundations of Design and Entrepreneurship I
    (2, 1, 1, 'I', 'CS111');       -- Introduction to Computing and Information Systems

-- Semester 1
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 1, 'II', 'AS111'),      -- Ashesi Success
    (2, 1, 1, 'II', 'MATH141'),    -- Calculus 1
    (2, 1, 1, 'II', 'ENGL112'),    -- Written and Oral Communication
    (2, 1, 1, 'II', 'BUSA161'),    -- Foundations of Design and Entrepreneurship I
    (2, 1, 1, 'II', 'CS111');      -- Introduction to Computing and Information Systems

-- Semester 2
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 2, 'I', 'SOAN111'),      -- Leadership Seminar 1: What Makes a Good Leader?
    (2, 1, 2, 'I', 'MATH122'),      -- Pre-calculus 2
    (2, 1, 2, 'I', 'ENGL113'),      -- Text & Meaning
    (2, 1, 2, 'I', 'BUSA162'),      -- Foundations of Design and Entrepreneurship II
    (2, 1, 2, 'I', 'CS212');        -- Computer Programming for Computer Science

-- Semester 2
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 2, 'II', 'SOAN111'),     -- Leadership Seminar 1: What Makes a Good Leader?
    (2, 1, 2, 'II', 'MATH142'),     -- Calculus 2
    (2, 1, 2, 'II', 'ENGL113'),     -- Text & Meaning
    (2, 1, 2, 'II', 'BUSA162'),     -- Foundations of Design and Entrepreneurship II
    (2, 1, 2, 'II', 'CS212');       -- Computer Programming for Computer Science

-- Year 2
-- Semester 3
-- No Type
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 2, 3, '', 'SOAN211'),       -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (2, 2, 3, '', 'MATH221'),       -- Statistics with Probability
    (2, 2, 3, '', 'ECON100'),       -- Principles of Economics
    (2, 2, 3, '', 'CS213'),         -- Object-Oriented Programming
    (2, 2, 3, '', 'CS221');         -- Discrete Structures and Theory

-- Semester 4
-- No Type
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 2, 4, '', 'MATH212'),       -- Linear Algebra
    (2, 2, 4, '', 'SOAN311'),       -- Leadership Seminar 3: The Economic Development of a Good Society
    (2, 2, 4, '', 'CS222'),         -- Data Structures and Algorithms
    (2, 2, 4, '', 'CS323'),         -- Database Systems
    (2, 2, 4, '', 'CS254');         -- Introduction to Artificial Intelligence

-- Year 3
-- Semester 5
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 5, 'I', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (2, 3, 5, 'I', 'CS341'),        -- Web Development
    (2, 3, 5, 'I', 'CS456'),        -- Algorithm Design & Analysis
    (2, 3, 5, 'I', 'CS313'),        -- Intermediate Computer Programming
    (2, 3, 5, 'I', 'CS330');        -- Hardware and Systems Fundamentals

-- Semester 5
-- Type II (Major Elective)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 5, 'II', 'CS341'),       -- Web Development
    (2, 3, 5, 'II', 'CS456'),       -- Algorithm Design & Analysis
    (2, 3, 5, 'II', 'CS313'),       -- Intermediate Computer Programming
    (2, 3, 5, 'II', 'CS330');       -- Hardware and Systems Fundamentals

-- Semester 6
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 6, 'I', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (2, 3, 6, 'I', 'CS415'),        -- Software Engineering
    (2, 3, 6, 'I', 'CS331'),        -- Computer Architecture
    (2, 3, 6, 'I', 'SOAN325'),      -- Research Methods
    (2, 3, 6, 'I', 'CS361');        -- Introduction to Modelling and Simulation

-- Semester 6
-- Type II (Major Elective)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 6, 'II', 'CS415'),       -- Software Engineering
    (2, 3, 6, 'II', 'CS331'),       -- Computer Architecture
    (2, 3, 6, 'II', 'SOAN325'),     -- Research Methods
    (2, 3, 6, 'II', 'CS361');       -- Introduction to Modelling and Simulation

-- Year 4
-- Semester 7
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'I', 'CS433'),        -- Operating Systems and Systems Administration
    (2, 4, 7, 'I', 'BUSA224'),      -- Finance for Non-Finance
    (2, 4, 7, 'I', 'CS402'),        -- CSIS Research Seminar
    (2, 4, 7, 'I', 'CS400_A');      -- Thesis I

-- Semester 7
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'II', 'CS433'),       -- Operating Systems and Systems Administration
    (2, 4, 7, 'II', 'BUSA224'),     -- Finance for Non-Finance
    (2, 4, 7, 'II', 'CS402'),       -- CSIS Research Seminar
    (2, 4, 7, 'II', 'ELECTIVE2');   -- Extra Major Elective

-- Semester 7
-- Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'III', 'CS433'),      -- Operating Systems and Systems Administration
    (2, 4, 7, 'III', 'BUSA224'),    -- Finance for Non-Finance
    (2, 4, 7, 'III', 'CS402');      -- CSIS Research Seminar

-- Semester 7
-- Type IV
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'IV', 'CS433'),       -- Operating Systems and Systems Administration
    (2, 4, 7, 'IV', 'BUSA224'),     -- Finance for Non-Finance
    (2, 4, 7, 'IV', 'CS402'),       -- CSIS Research Seminar
    (2, 4, 7, 'IV', 'BUSA401_A');   -- Entrepreneurship I (Capstone)

-- Semester 8
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'I', 'CS432'),        -- Computer Networks and Data Communications
    (2, 4, 8, 'I', 'ELECTIVE1'),    -- Elective (4 credits)
    (2, 4, 8, 'I', 'ELECTIVE1'),    -- Elective (4 credits)
    (2, 4, 8, 'I', 'CS400_B');      -- Thesis II

-- Semester 8
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'II', 'CS432'),       -- Computer Networks and Data Communications
    (2, 4, 8, 'II', 'ELECTIVE1'),   -- Elective (4 credits)
    (2, 4, 8, 'II', 'ELECTIVE1'),   -- Elective (4 credits)
    (2, 4, 8, 'II', 'CS410');       -- Applied Project

-- Semester 8
-- Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'III', 'CS432'),      -- Computer Networks and Data Communications
    (2, 4, 8, 'III', 'ELECTIVE1'),  -- Elective (4 credits)
    (2, 4, 8, 'III', 'ELECTIVE1'),  -- Elective (4 credits)
    (2, 4, 8, 'III', 'BUSA401_A');  -- Entrepreneurship I (Capstone)

-- MIS

-- Year 1 Semester 1 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 1, 'I', 'AS111'),    -- Ashesi Success
    (3, 1, 1, 'I', 'MATH121'),  -- Pre-calculus 1
    (3, 1, 1, 'I', 'ENGL112'),  -- Written and Oral Communication
    (3, 1, 1, 'I', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
    (3, 1, 1, 'I', 'CS111');    -- Introduction to Computing and Information Systems

-- Year 1 Semester 1 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 1, 'II', 'AS111'),    -- Ashesi Success
    (3, 1, 1, 'II', 'MATH141'),  -- Calculus 1
    (3, 1, 1, 'II', 'ENGL112'),  -- Written and Oral Communication
    (3, 1, 1, 'II', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
    (3, 1, 1, 'II', 'CS111');    -- Introduction to Computing and Information Systems

-- Year 1 Semester 2 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 2, 'I', 'SOAN111'),  -- Leadership Seminar 1: What Makes a Good Leader?
    (3, 1, 2, 'I', 'MATH122'),  -- Pre-calculus 2
    (3, 1, 2, 'I', 'ENGL113'),  -- Text & Meaning
    (3, 1, 2, 'I', 'BUSA162'),  -- Foundations of Design and Entrepreneurship II
    (3, 1, 2, 'I', 'CS212');    -- Computer Programming for Computer Science

-- Year 1 Semester 2 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 2, 'II', 'SOAN111'),  -- Leadership Seminar 1: What Makes a Good Leader?
    (3, 1, 2, 'II', 'MATH142'),  -- Calculus 2
    (3, 1, 2, 'II', 'ENGL113'),  -- Text & Meaning
    (3, 1, 2, 'II', 'BUSA162'),  -- Foundations of Design and Entrepreneurship II
    (3, 1, 2, 'II', 'CS212');    -- Computer Programming for Computer Science

-- Year 2 Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 3, '', 'SOAN211'),   -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (3, 2, 3, '', 'MATH221'),   -- Statistics with Probability
    (3, 2, 3, '', 'ECON100'),   -- Principles of Economics
    (3, 2, 3, '', 'CS213'),     -- Object-Oriented Programming
    (3, 2, 3, '', 'CS221');     -- Discrete Structures and Theory

-- Year 2 Semester 4 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 4, 'I', 'MATH143'),   -- Quantitative Methods
    (3, 2, 4, 'I', 'SOAN311'),   -- Leadership Seminar 3: The Economic Development of a Good Society
    (3, 2, 4, 'I', 'CS222'),     -- Data Structures and Algorithms
    (3, 2, 4, 'I', 'CS323'),     -- Database Systems
    (3, 2, 4, 'I', 'CS254');     -- Introduction to Artificial Intelligence

-- Year 2 Semester 4 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 4, 'II', 'MATH143'),    -- Quantitative Methods
    (3, 2, 4, 'II', 'SOAN311'),    -- Leadership Seminar 3: The Economic Development of a Good Society
    (3, 2, 4, 'II', 'ELECTIVE1'),  -- Non-Major Elective
    (3, 2, 4, 'II', 'CS323'),      -- Database Systems
    (3, 2, 4, 'II', 'CS254');      -- Introduction to Artificial Intelligence

-- Year 3 Semester 5 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 5, 'I', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (3, 3, 5, 'I', 'CS341'),      -- Web Development (Elective)
    (3, 3, 5, 'I', 'IS351'),      -- Systems Analysis and Design
    (3, 3, 5, 'I', 'BUSA224');    -- Finance for Non-Finance

-- Year 3 Semester 5 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 5, 'II', 'ELECTIVE1'),  -- Major Elective (4 credits)
    (3, 3, 5, 'II', 'CS341'),      -- Web Development (Elective)
    (3, 3, 5, 'II', 'IS351'),      -- Systems Analysis and Design
    (3, 3, 5, 'II', 'BUSA224');    -- Finance for Non-Finance

-- Year 3 Semester 6 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 6, 'I', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (3, 3, 6, 'I', 'CS415'),      -- Software Engineering
    (3, 3, 6, 'I', 'CS331'),      -- Computer Architecture
    (3, 3, 6, 'I', 'SOAN325'),    -- Research Methods
    (3, 3, 6, 'I', 'CS361');      -- Introduction to Modelling and Simulation

-- Year 3 Semester 6 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 6, 'II', 'ELECTIVE1'),  -- Major Elective (4 credits)
    (3, 3, 6, 'II', 'CS415'),      -- Software Engineering
    (3, 3, 6, 'II', 'CS331'),      -- Computer Architecture
    (3, 3, 6, 'II', 'SOAN325'),    -- Research Methods
    (3, 3, 6, 'II', 'CS361');      -- Introduction to Modelling and Simulation

-- Year 4 Semester 7 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'I', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'I', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'I', 'ELECTIVE1'),   -- Elective (4 credits)
    (3, 4, 7, 'I', 'BUSA400_A');   -- Thesis 1

-- Year 4 Semester 7 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'II', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'II', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'II', 'ELECTIVE1'),   -- Elective (4 credits)
    (3, 4, 7, 'II', 'BUSA401_A');   -- Entrepreneurship I (Capstone)

-- Year 4 Semester 7 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'III', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'III', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'III', 'ELECTIVE1'),   -- Elective (4 credits)
    (3, 4, 7, 'III', 'ELECTIVE2');   -- Extra Major Elective

-- Year 4 Semester 7 - Type IV
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'IV', 'CS442'),        -- E-Commerce (Elective)
    (3, 4, 7, 'IV', 'IS451'),        -- Information and Systems Security (Elective)
    (3, 4, 7, 'IV', 'ELECTIVE1'),    -- Elective (4 credits)
    (3, 4, 7, 'IV', 'CS400_A'),      -- Thesis I (Capstone)
    (3, 4, 7, 'IV', 'BUSA401_A');    -- Entrepreneurship I (Capstone)

-- Year 4 Semester 7 - Type V
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'V', 'CS442'),        -- E-Commerce (Elective)
    (3, 4, 7, 'V', 'IS451'),        -- Information and Systems Security (Elective)
    (3, 4, 7, 'V', 'ELECTIVE1'),    -- Elective (4 credits)
    (3, 4, 7, 'V', 'BUSA401_A');    -- Entrepreneurship I (Capstone)

-- Year 4 Semester 7 - Type VI
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'VI', 'CS442'),        -- E-Commerce (Elective)
    (3, 4, 7, 'VI', 'IS451'),        -- Information and Systems Security (Elective)
    (3, 4, 7, 'VI', 'ELECTIVE1'),    -- Elective (4 credits)
    (3, 4, 7, 'VI', 'ELECTIVE2');    -- Extra Major Elective

-- Year 4 Semester 8 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'I', 'CS432'),         -- Computer Networks and Data Communications
    (3, 4, 8, 'I', 'ELECTIVE1'),     -- Elective (4 credits)
    (3, 4, 8, 'I', 'ELECTIVE1'),     -- Elective (4 credits)
    (3, 4, 8, 'I', 'CS400_B');       -- Thesis II

-- Year 4 Semester 8 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'II', 'CS432'),         -- Computer Networks and Data Communications
    (3, 4, 8, 'II', 'ELECTIVE1'),     -- Elective (4 credits)
    (3, 4, 8, 'II', 'ELECTIVE1'),     -- Elective (4 credits)
    (3, 4, 8, 'II', 'CS410');         -- Applied Project

-- Year 4 Semester 8 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'III', 'CS432'),        -- Computer Networks and Data Communications
    (3, 4, 8, 'III', 'ELECTIVE1'),    -- Elective (4 credits)
    (3, 4, 8, 'III', 'ELECTIVE1'),    -- Elective (4 credits)
    (3, 4, 8, 'III', 'BUSA401_B');    -- Entrepreneurship II (Capstone)


--COMPUTER ENGINEERING

-- ----------------------------------------------------
-- Insert Correct ProgramPlan Entries for Computer Engineering (MajorID = 4)
-- ----------------------------------------------------

-- Year 1, Semester 1 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 1, 1, '', 'AS111'),      -- Ashesi Success
    (4, 1, 1, '', 'ENGL112'),    -- Written and Oral Communication
    (4, 1, 1, '', 'BUSA161'),    -- Foundations of Design and Entrepreneurship I
    (4, 1, 1, '', 'ENGR112'),    -- Introduction to Engineering
    (4, 1, 1, '', 'MATH161');    -- Engineering Calculus

-- Year 1, Semester 2 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 1, 2, '', 'CS112'),      -- Computer Programming for Engineering
    (4, 1, 2, '', 'MATH211'),    -- Multivariable Calculus and Linear Algebra
    (4, 1, 2, '', 'BUSA162'),    -- Foundations of Design and Entrepreneurship II
    (4, 1, 2, '', 'ME101'),      -- Introduction to Mechanics
    (4, 1, 2, '', 'SOAN111');    -- Leadership Seminar 1: What Makes a Good Leader?

-- Year 2, Semester 3 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 2, 3, '', 'SC113'),      -- Physics II: Electromagnetism
    (4, 2, 3, '', 'MATH152'),    -- Statistics for Engineering and Economics
    (4, 2, 3, '', 'CS221'),      -- Discrete Structures and Theory
    (4, 2, 3, '', 'CS213'),      -- Object-Oriented Programming
    (4, 2, 3, '', 'SOAN211');    -- Leadership Seminar 2: Rights, Ethics, and Rule of Law

-- Year 2, Semester 4 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 2, 4, '', 'MATH251'),    -- Differential Equations & Numerical Methods
    (4, 2, 4, '', 'SOAN311'),    -- Leadership Seminar 3: The Economic Development of a Good Society
    (4, 2, 4, '', 'EE222'),      -- Circuits and Electronics
    (4, 2, 4, '', 'SC221'),      -- Materials Science & Chemistry
    (4, 2, 4, '', 'ENGL113'),    -- Text & Meaning
    (4, 2, 4, '', 'CE122');      -- Applied Programming for Engineers

-- Year 3, Semester 5 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 3, 5, '', 'CS331'),      -- Computer Architecture
    (4, 3, 5, '', 'ENGR311'),    -- System Dynamics
    (4, 3, 5, '', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (4, 3, 5, '', 'ENGR212'),    -- Instrumentation for Engineering
    (4, 3, 5, '', 'ENGR300'),    -- Third Year Group Project & Seminar
    (4, 3, 5, '', 'EE320');      -- Signals & Systems

-- Year 3, Semester 6 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 3, 6, '', 'ENGR312'),           -- Control Systems
    (4, 3, 6, '', 'CS432'),             -- Networks and Distributed Computing
    (4, 3, 6, '', 'CS222'),             -- Data Structures and Algorithms
    (4, 3, 6, '', 'CE322'),             -- Digital Systems Design
    (4, 3, 6, '', 'ELECTIVE1');         -- Elective (4 credits)

-- Year 4, Semester 7 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 4, 7, '', 'CS433'),            -- Operating Systems and Systems Administration
    (4, 4, 7, '', 'ELECTIVE1'),        -- CE Elective (4 credits)
    (4, 4, 7, '', 'ECON100'),          -- Principles of Economics
    (4, 4, 7, '', 'CE451'),            -- Embedded Systems
    (4, 4, 7, '', 'ELECTIVE2');        -- Elective (4 credits)

-- Year 4, Semester 8 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 4, 8, '', 'ENGR413'),           -- Project Management & Professional Practice
    (4, 4, 8, '', 'ELECTIVE1'),         -- CE Elective
    (4, 4, 8, '', 'ELECTIVE2'),         -- African Studies Elective
    (4, 4, 8, '', 'ENGR401');           -- Senior Project and Seminar


--MECHANICAL ENGINEERING

-- Year 1
-- Semester 1
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 1, 1, '', 'AS111'),        -- Ashesi Success
    (6, 1, 1, '', 'ENGL112'),      -- Written and Oral Communication
    (6, 1, 1, '', 'BUSA161'),      -- Foundations of Design and Entrepreneurship I
    (6, 1, 1, '', 'ENGR112'),      -- Introduction to Engineering
    (6, 1, 1, '', 'MATH161');      -- Engineering Calculus

-- Semester 2
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 1, 2, '', 'CS112'),        -- Computer Programming for Engineering
    (6, 1, 2, '', 'MATH211'),      -- Multivariable Calculus and Linear Algebra
    (6, 1, 2, '', 'BUSA162'),      -- Foundations of Design and Entrepreneurship II
    (6, 1, 2, '', 'ME101'),        -- Introduction to Mechanics
    (6, 1, 2, '', 'SOAN111');      -- Leadership Seminar 1: What Makes a Good Leader?

-- Year 2
-- Semester 3
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 2, 3, '', 'SC113'),        -- Physics II: Electromagnetism
    (6, 2, 3, '', 'ME201'),        -- Thermodynamics
    (6, 2, 3, '', 'MATH152'),      -- Statistics for Engineering and Economics
    (6, 2, 3, '', 'SOAN211'),      -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (6, 2, 3, '', 'ME442');        -- Computer Aided Design (CAD) / Manufacturing (CAM)

-- Semester 4
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 2, 4, '', 'MATH251'),      -- Differential Equations & Numerical Methods
    (6, 2, 4, '', 'SOAN311'),      -- Leadership Seminar 3: The Economic Development of a Good Society
    (6, 2, 4, '', 'EE222'),        -- Circuits and Electronics
    (6, 2, 4, '', 'SC221'),        -- Materials Science & Chemistry
    (6, 2, 4, '', 'ENGL113'),      -- Text & Meaning
    (6, 2, 4, '', 'CE122');        -- Applied Programming for Engineers

-- Year 3
-- Semester 5
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 3, 5, '', 'EE341'),        -- AC Electrical Machines
    (6, 3, 5, '', 'ENGR311'),      -- System Dynamics
    (6, 3, 5, '', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (6, 3, 5, '', 'ENGR212'),      -- Instrumentation for Engineering
    (6, 3, 5, '', 'ENGR300'),      -- Third Year Group Project & Seminar
    (6, 3, 5, '', 'EE320');        -- Signals & Systems

-- Semester 6
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 3, 6, '', 'ENGR312'),      -- Control Systems
    (6, 3, 6, '', 'ME301'),        -- Mechanical Machine Design
    (6, 3, 6, '', 'ME411'),        -- Fluid Mechanics
    (6, 3, 6, '', 'ME441'),        -- Manufacturing Processes
    (6, 3, 6, '', 'ELECTIVE1');    -- ME Elective

-- Year 4
-- Semester 7
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 4, 7, '', 'ME311'),        -- Mechanics of Materials/Structural Engineering
    (6, 4, 7, '', 'ME340'),        -- Heat and Mass Transfer
    (6, 4, 7, '', 'ECON100'),      -- Principles of Economics
    (6, 4, 7, '', 'CE451'),        -- Embedded Systems
    (6, 4, 7, '', 'ELECTIVE1');    -- Elective (4 credits)

-- Semester 8
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 4, 8, '', 'ENGR413'),      -- Project Management & Professional Practice
    (6, 4, 8, '', 'ELECTIVE1'),    -- ME Elective
    (6, 4, 8, '', 'ELECTIVE1'),    -- African Studies Elective
    (6, 4, 8, '', 'ENGR401');      -- Senior Project and Seminar (Capstone)





-- MySQL dump 10.13  Distrib 5.5.62, for Linux (x86_64)
--
-- Host: localhost    Database: nzoly
-- ------------------------------------------------------
-- Server version	5.5.62-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `event_stage`
--

DROP TABLE IF EXISTS `event_stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_stage` (
  `StageID` int(11) NOT NULL AUTO_INCREMENT,
  `StageName` varchar(50) NOT NULL,
  `EventID` int(11) NOT NULL,
  `Location` varchar(50) NOT NULL,
  `StageDate` date NOT NULL,
  `Qualifying` tinyint(1) NOT NULL,
  `PointsToQualify` float DEFAULT NULL,
  PRIMARY KEY (`StageID`),
  KEY `EventID` (`EventID`),
  CONSTRAINT `event_stage_ibfk_1` FOREIGN KEY (`EventID`) REFERENCES `events` (`EventID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=392 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_stage`
--

LOCK TABLES `event_stage` WRITE;
/*!40000 ALTER TABLE `event_stage` DISABLE KEYS */;
INSERT INTO `event_stage` VALUES (281,'Qualification',7,'Genting Snow Park','2022-02-14',1,63.4),(289,'Qualification',11,'Genting Snow Park','2022-02-17',1,70),(290,'Final',11,'Genting Snow Park','2022-02-19',0,NULL),(356,'Heat 1',3,'Shougang','2022-02-14',1,127.5),(357,'Final',3,'Shougang','2022-02-15',0,NULL),(377,'Heat 1',1,'Genting Snow Park','2022-02-05',1,65),(379,'Final',1,'Genting Snow Park','2022-02-06',0,NULL);
/*!40000 ALTER TABLE `event_stage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_stage_results`
--

DROP TABLE IF EXISTS `event_stage_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_stage_results` (
  `ResultID` int(11) NOT NULL AUTO_INCREMENT,
  `StageID` int(11) NOT NULL,
  `MemberID` int(11) NOT NULL,
  `PointsScored` float NOT NULL,
  `Position` int(11) DEFAULT NULL,
  PRIMARY KEY (`ResultID`),
  KEY `StageID` (`StageID`),
  KEY `MemberID` (`MemberID`),
  CONSTRAINT `event_stage_results_ibfk_1` FOREIGN KEY (`StageID`) REFERENCES `event_stage` (`StageID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `event_stage_results_ibfk_2` FOREIGN KEY (`MemberID`) REFERENCES `members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=586 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_stage_results`
--

LOCK TABLES `event_stage_results` WRITE;
/*!40000 ALTER TABLE `event_stage_results` DISABLE KEYS */;
INSERT INTO `event_stage_results` VALUES (222,289,5633,90.5,NULL),(223,290,5633,93,1),(265,281,5632,54.93,NULL),(467,356,5634,176.5,NULL),(538,357,5634,177,2),(567,377,5634,86.75,NULL),(577,379,5634,92.88,1);
/*!40000 ALTER TABLE `event_stage_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `EventID` int(11) NOT NULL AUTO_INCREMENT,
  `EventName` varchar(80) NOT NULL,
  `Sport` varchar(50) NOT NULL,
  `NZTeam` int(11) DEFAULT NULL,
  PRIMARY KEY (`EventID`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'Slopestyle','Snowboarding',101),(3,'Big Air','Snowboarding',101),(5,'Men\'s Halfpipe','Freestyle Skiing',103),(6,'Men\'s 20 km individual biathlon','Biathlon',123),(7,'Women\'s slopestyle','Freestyle Skiing',103),(11,'Men\'s Halfpipe','Snowboarding',101);
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members` (
  `MemberID` int(11) NOT NULL AUTO_INCREMENT,
  `TeamID` int(11) NOT NULL,
  `FirstName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `City` varchar(30) DEFAULT NULL,
  `Birthdate` date NOT NULL,
  PRIMARY KEY (`MemberID`),
  KEY `TeamID` (`TeamID`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`TeamID`) REFERENCES `teams` (`TeamID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5651 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (5629,103,'Ben','Barclay','Auckland','2002-02-04'),(5630,103,'Anja','Barugh','Morrinsville','1999-05-21'),(5631,103,'Finn','Bilous','Wanaka','1999-09-22'),(5632,103,'Margaux','Hackett','Wanaka','1999-06-02'),(5633,103,'Nico','Porteous','Hamilton','2001-11-23'),(5634,101,'Zoi','Sadowski-Synnott','Wanaka','2001-03-06'),(5635,101,'Tiarn','Collins','Queenstown','1999-11-09'),(5636,125,'Peter','Michael','Wellington','1989-05-09'),(5637,123,'Campbell','Wright','Rotorua','2002-05-25');
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teams` (
  `TeamID` int(11) NOT NULL AUTO_INCREMENT,
  `TeamName` varchar(80) NOT NULL,
  PRIMARY KEY (`TeamID`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teams`
--

LOCK TABLES `teams` WRITE;
/*!40000 ALTER TABLE `teams` DISABLE KEYS */;
INSERT INTO `teams` VALUES (101,'Snowboard'),(102,'Alpine Skiing'),(103,'Freestyle Skiing'),(123,'Biathlon'),(125,'Speed Skating');
/*!40000 ALTER TABLE `teams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'nzoly'
--

--
-- Dumping routines for database 'nzoly'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-11 11:46:00

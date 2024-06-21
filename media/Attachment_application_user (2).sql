-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 19, 2024 at 10:46 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rit_e_approval`
--

-- --------------------------------------------------------

--
-- Table structure for table `application_user`
--

CREATE TABLE `application_user` (
  `id` bigint(20) NOT NULL,
  `Name` varchar(100) NOT NULL,
  `user_name` varchar(100) NOT NULL,
  `staff_id` varchar(100) NOT NULL,
  `Department` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` varchar(100) NOT NULL,
  `Password` varchar(100) NOT NULL,
  `confirm_Password` varchar(100) NOT NULL,
  `Department_code` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `application_user`
--

INSERT INTO `application_user` (`id`, `Name`, `user_name`, `staff_id`, `Department`, `email`, `role`, `Password`, `confirm_Password`, `Department_code`) VALUES
(1, 'Technician', 'Technician', '1111', 'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE', 'adtech@ritrjpm.ac.in', 'Technician', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(2, 'AD_HOD', 'AD_HOD', '2222', 'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE', '953622243021@ritrjpm.ac.in', 'HOD', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(3, 'GM_ADMIN', 'GM_ADMIN', '3333', 'Office', '953621243053@ritrjpm.ac.in', 'GM', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(4, 'VICE_PRINCIPLE', 'VICE_PRINCIPLE', '4444', 'Office', 'dhaneshponraj@gmail.com', 'vice_principal', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(5, 'STAFF', 'STAFF', '5555', 'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE', 'pavotigris9218@gmail.com', 'Staff', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(6, 'PRINCIPAL', 'PRINCIPAL', '6666', 'Office', '953621243014@ritrjpm.ac.in', 'Principal', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(7, 'Hash', 'mech_hod', '7777', 'MECHANICAL ENGINEERING', 'mechhod@ritrjpm.ac.in', 'HOD', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(8, 'mech_tech', 'mech_tech', '8888', 'MECHANICAL ENGINEERING', 'mechtech@ritrjpm.ac.in', 'Technician', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', ''),
(9, 'cse_tech', 'cse_tech', '9999', 'COMPUTER SCIENCE AND ENGINEERING', 'csetech@ritrjpm.ac.in', 'Technician', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `application_user`
--
ALTER TABLE `application_user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `application_user`
--
ALTER TABLE `application_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

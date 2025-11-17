-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 17, 2025 at 04:29 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mode7app`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `order_number` varchar(50) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `status` enum('pending','processing','completed','cancelled') DEFAULT 'pending',
  `delivery_address` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `delivery_lat` decimal(10,7) DEFAULT NULL,
  `delivery_lng` decimal(10,7) DEFAULT NULL,
  `stock_deducted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `order_number`, `buyer_id`, `seller_id`, `product_id`, `quantity`, `total_price`, `status`, `delivery_address`, `created_at`, `updated_at`, `delivery_lat`, `delivery_lng`, `stock_deducted`) VALUES
(5, 'ORD-20251104151631-5316', 7, 6, 26, 3, 27000.00, 'completed', 'ewqewq, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-04 07:16:31', '2025-11-04 07:56:20', NULL, NULL, 1),
(6, 'ORD-20251104154257-4811', 7, 6, 25, 1, 200.00, 'completed', 'ewqewq, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-04 07:42:57', '2025-11-17 14:43:05', 14.2639100, 121.4054400, 1),
(7, 'ORD-20251117140418-5099', 7, 6, 27, 1, 1000.00, 'completed', 'ewqewq, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-17 06:04:18', '2025-11-17 14:43:12', 13.9413890, 121.6234510, 1),
(8, 'ORD-20251117230953-1868', 7, 6, 27, 1, 1000.00, '', 'DapDap Road, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-17 15:09:53', '2025-11-17 15:09:53', 13.9413890, 121.6234510, 0),
(9, 'ORD-20251117231022-8235', 7, 6, 25, 1, 200.00, '', 'DapDap Road, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-17 15:10:22', '2025-11-17 15:10:22', 13.9413890, 121.6234510, 0),
(10, 'ORD-20251117231928-2153', 7, 6, 26, 1, 9000.00, 'completed', 'DapDap Road, Biñan, Pagsanjan, Laguna, CALABARZON, 4033', '2025-11-17 15:19:28', '2025-11-17 15:19:44', 13.9413890, 121.6234510, 1);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) DEFAULT 0,
  `category` varchar(100) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `weight` decimal(10,2) DEFAULT NULL,
  `sku` varchar(100) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `seller_id`, `name`, `description`, `price`, `stock`, `category`, `brand`, `size`, `color`, `weight`, `sku`, `image`, `status`, `created_at`, `updated_at`) VALUES
(7, 6, 'Black Trimmer', 'trimmer', 500.00, 5, 'Grooming Products', '', '', 'Black', 0.00, '', '00b880291c6d4c029017afd7f893a690_Black_Trimmer_2.png', 'active', '2025-11-04 04:53:59', '2025-11-04 04:53:59'),
(8, 6, 'Shaving Foam', 'foam', 50.00, 2, 'Grooming Products', '', '', '', 0.00, '', '029b1711dd3c4d4688e13b841e33a30d_Shaving_Foam.png', 'active', '2025-11-04 04:55:08', '2025-11-04 04:55:08'),
(9, 6, 'Black Pants', '', 250.00, 10, 'Casual Shirts & Pants', '', '', 'Black', 0.00, '', '20eedb5a46d84d89a872ba90713d1e2e_Black_Pants.png', 'active', '2025-11-04 06:19:44', '2025-11-04 06:19:44'),
(10, 6, 'Black Shirt', '', 100.00, 20, 'Casual Shirts & Pants', '', '', 'Black', 0.00, '', 'f6dd93bda5c740deabce56558a11ddcf_Black_Shirt_2.png', 'active', '2025-11-04 06:20:17', '2025-11-04 06:20:17'),
(11, 6, 'Blue Shirt', '', 150.00, 15, 'Casual Shirts & Pants', '', '', 'Blue', 0.00, '', 'f47ef5aaf90a42e8ab2e5441e8cdf9b7_Blue_Shirt_2.png', 'active', '2025-11-04 06:20:45', '2025-11-04 06:20:45'),
(12, 6, 'Green Pants', '', 300.00, 7, 'Casual Shirts & Pants', '', '', 'Green', 0.00, '', '26df9e964d9f4a968568359a03e32103_Green_Pants_2.png', 'active', '2025-11-04 06:21:16', '2025-11-04 06:21:16'),
(13, 6, 'Grey Shirt', '', 150.00, 9, 'Casual Shirts & Pants', '', '', 'Grey', 0.00, '', '2a690cd125e84cc78a990cacc05f8001_Grey_Shirt_2.png', 'active', '2025-11-04 06:21:43', '2025-11-04 06:21:43'),
(14, 6, 'Rinse Wash Pants', '', 400.00, 6, 'Casual Shirts & Pants', '', '', '', 0.00, '', 'af027251806f4eabb8bf12659e2be3f4_Rinse_Wash_Pants_2.png', 'active', '2025-11-04 06:22:08', '2025-11-04 06:22:08'),
(15, 6, 'Dark Brown Blazer', '', 500.00, 6, 'Suits & Blazers', '', '', 'Dark Brown', 0.00, '', '2999525282694275884490006a211f53_Dark_Brown_Blazer_2.png', 'active', '2025-11-04 06:22:52', '2025-11-04 06:22:52'),
(16, 6, 'Black Suit', '', 400.00, 8, 'Suits & Blazers', '', '', 'Black', 0.00, '', '99b217bd964a49d0a4761146a9305f7b_Black_Suit_2.png', 'active', '2025-11-04 06:23:25', '2025-11-04 06:23:25'),
(17, 6, 'Grey Suit', '', 400.00, 9, 'Suits & Blazers', '', '', 'Grey', 0.00, '', '8d56ef481c0849f2b7ae70a322a0ec2d_Grey_Suit_2.png', 'active', '2025-11-04 06:23:50', '2025-11-04 06:23:50'),
(18, 6, 'Olive Green Suit', '', 400.00, 10, 'Suits & Blazers', '', '', 'Olive Green', 0.00, '', '2a3f3ec9029140b7a03477ac0770833f_Olive_Green_Suit.png', 'active', '2025-11-04 06:24:58', '2025-11-04 06:24:58'),
(19, 6, 'Navy Blazer', '', 400.00, 16, 'Suits & Blazers', '', '', 'Navy', 0.00, '', '2b51bccc57a54cbabc463412a39b841a_Navy_Blazer_2.png', 'active', '2025-11-04 06:25:30', '2025-11-04 06:25:30'),
(20, 6, 'Black Bomber', '', 300.00, 7, 'Outerwear & Jackets', '', '', 'Black', 0.00, '', '2ab2cc736bb04ee2889996b1e8ac7d12_Black_Bomber_2.png', 'active', '2025-11-04 06:26:05', '2025-11-04 06:26:05'),
(21, 6, 'Blue Bomber', '', 300.00, 8, 'Outerwear & Jackets', '', '', 'Blue', 0.00, '', 'd0dd2168ab184d13bbc2da6b3adc6503_Blue_Bomber_2.png', 'active', '2025-11-04 06:26:43', '2025-11-04 06:26:43'),
(22, 6, 'Brown Jacket', '', 300.00, 9, 'Outerwear & Jackets', '', '', 'Brown', 0.00, '', 'c0834cc022b945738196d7d12ac17048_Brown_Jacket_2.png', 'active', '2025-11-04 06:28:02', '2025-11-04 06:28:02'),
(23, 6, 'Grey Vest', '', 450.00, 5, 'Outerwear & Jackets', '', '', 'Grey', 0.00, '', '5efabac0f0bf4d70961c54ea93b72465_Grey_Vest_2.png', 'active', '2025-11-04 06:28:30', '2025-11-04 06:28:30'),
(24, 6, 'Navy Jacket', '', 300.00, 14, 'Outerwear & Jackets', '', '', 'Navy', 0.00, '', '687c790c5b254b86b8635a5311046e9e_Navy_Jacket_1.png', 'active', '2025-11-04 06:29:02', '2025-11-04 06:29:02'),
(25, 6, 'Grey Trunks', '', 200.00, 8, 'Activewear & Fitness Gear', '', '', 'Grey', 0.00, '', 'f8fa0047de3c4de18d02790ef0ac6a57_Grey_Trunks_2.png', 'active', '2025-11-04 06:29:52', '2025-11-17 14:42:57'),
(26, 6, 'Adidas Samba', '', 9000.00, 2, 'Shoes & Accessories', 'Adidas', '', '', 0.00, '', '474df0d340b0497b83252bd06a3eda84_Adidas_Samba_2.png', 'active', '2025-11-04 06:30:35', '2025-11-17 15:19:42'),
(27, 6, 'Columbia Wallet', '', 1000.00, 7, 'Shoes & Accessories', 'Columbia', '', '', 0.00, '', '3bef80e8a2094fcbb3545544c94e86bc_Columbia_Wallet_2.png', 'active', '2025-11-04 06:31:12', '2025-11-17 14:43:10');

-- --------------------------------------------------------

--
-- Table structure for table `product_images`
--

CREATE TABLE `product_images` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `image` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_images`
--

INSERT INTO `product_images` (`id`, `product_id`, `image`, `created_at`) VALUES
(1, 7, '00b880291c6d4c029017afd7f893a690_Black_Trimmer_2.png', '2025-11-04 04:53:59'),
(2, 7, 'da462c8f8c8946c6b5e01e6f981f566c_Black_Trimmer.png', '2025-11-04 04:53:59'),
(3, 8, '029b1711dd3c4d4688e13b841e33a30d_Shaving_Foam.png', '2025-11-04 04:55:08'),
(4, 9, '20eedb5a46d84d89a872ba90713d1e2e_Black_Pants.png', '2025-11-04 06:19:44'),
(5, 9, '60395a4eed3d4395be904764073c7693_Black_Pants_2.png', '2025-11-04 06:19:44'),
(6, 9, '387974a7f8764ea98bc40b59f6273c8a_Black_Pants_3.png', '2025-11-04 06:19:44'),
(7, 10, 'f6dd93bda5c740deabce56558a11ddcf_Black_Shirt_2.png', '2025-11-04 06:20:17'),
(8, 10, 'a4cb58380059454784cfbaa709664655_Black_Shirt_3.png', '2025-11-04 06:20:17'),
(9, 10, 'eca8c0e817d34db0a8b2d16cc429fb31_Black_Shirt.png', '2025-11-04 06:20:17'),
(10, 11, 'f47ef5aaf90a42e8ab2e5441e8cdf9b7_Blue_Shirt_2.png', '2025-11-04 06:20:45'),
(11, 11, '29b8ccddd323406091e6d3bae2eb7705_Blue_Shirt_3.png', '2025-11-04 06:20:45'),
(12, 11, 'cbbec0c6b2914577a26e794b0747dfff_Blue_Shirt.png', '2025-11-04 06:20:45'),
(13, 12, '26df9e964d9f4a968568359a03e32103_Green_Pants_2.png', '2025-11-04 06:21:16'),
(14, 12, 'ed488f2228fd4910911d0f5a0c93a820_Green_Pants_3.png', '2025-11-04 06:21:16'),
(15, 12, 'c89addf570a044708b8ae3928d9f242f_Green_Pants.png', '2025-11-04 06:21:16'),
(16, 13, '2a690cd125e84cc78a990cacc05f8001_Grey_Shirt_2.png', '2025-11-04 06:21:43'),
(17, 13, 'f828a7d0409a44019fa9a231f01d8511_Grey_Shirt_3.png', '2025-11-04 06:21:43'),
(18, 13, 'fb4431cec6574067acd29f1d01fa06f1_Grey_Shirt.png', '2025-11-04 06:21:43'),
(19, 14, 'af027251806f4eabb8bf12659e2be3f4_Rinse_Wash_Pants_2.png', '2025-11-04 06:22:08'),
(20, 14, '75d12ed5d8e04753bdcb33a4c022d9a9_Rinse_Wash_Pants_3.png', '2025-11-04 06:22:08'),
(21, 14, 'ba2284529b4a49e4962570d84044b060_Rinse_Wash_Pants.png', '2025-11-04 06:22:08'),
(22, 15, '2999525282694275884490006a211f53_Dark_Brown_Blazer_2.png', '2025-11-04 06:22:52'),
(23, 15, '8d871a4e2e4149acb9eeb3e3f11e7942_Dark_Brown_Blazer_3.png', '2025-11-04 06:22:52'),
(24, 15, '5d66cc462fec4351a893a07a2ffcdb3b_Dark_Brown_Blazer.png', '2025-11-04 06:22:52'),
(25, 16, '99b217bd964a49d0a4761146a9305f7b_Black_Suit_2.png', '2025-11-04 06:23:25'),
(26, 16, '8f0c95ba701d4968964cb5c809752a2b_Black_Suit_3.png', '2025-11-04 06:23:25'),
(27, 16, '1a480d43665e480e813f8399a79d53b8_Black_Suit.png', '2025-11-04 06:23:25'),
(28, 17, '8d56ef481c0849f2b7ae70a322a0ec2d_Grey_Suit_2.png', '2025-11-04 06:23:50'),
(29, 17, '566035ef6db14f63be243a660a7f113e_Grey_Suit_3.png', '2025-11-04 06:23:50'),
(30, 17, '24f0c0715e8e440795139dac375dfb8b_Grey_Suit.png', '2025-11-04 06:23:50'),
(31, 18, '2a3f3ec9029140b7a03477ac0770833f_Olive_Green_Suit.png', '2025-11-04 06:24:58'),
(32, 18, '405c4baea437403395f1b221a9ecc750_Olive_Green_Suit_2.png', '2025-11-04 06:24:58'),
(33, 18, '1c194e3fe5b34eb88bab84fa192b4e59_Olive_Green_Suit_3.png', '2025-11-04 06:24:58'),
(34, 19, '2b51bccc57a54cbabc463412a39b841a_Navy_Blazer_2.png', '2025-11-04 06:25:30'),
(35, 19, 'c5b93f40722c41e3a19f3f6204826c5c_Navy_Blazer_3.png', '2025-11-04 06:25:30'),
(36, 19, 'a81892fb6e774a69ba660a29bda15894_Navy_Blazer.png', '2025-11-04 06:25:30'),
(37, 20, '2ab2cc736bb04ee2889996b1e8ac7d12_Black_Bomber_2.png', '2025-11-04 06:26:05'),
(38, 20, 'e00fca952b1e4c60899a9b6c58830eb2_Black_Bomber.png', '2025-11-04 06:26:05'),
(39, 20, '6fb04a6df82345928e6a80411be92299_Black_Bomber_3.png', '2025-11-04 06:26:05'),
(40, 21, 'd0dd2168ab184d13bbc2da6b3adc6503_Blue_Bomber_2.png', '2025-11-04 06:26:43'),
(41, 21, '4ef639cf0ae14345b889c6d10867f306_Blue_Bomber_3.png', '2025-11-04 06:26:43'),
(42, 21, 'bee39a2a24a846bfbc0dad10ba54e68b_Blue_Bomber.png', '2025-11-04 06:26:43'),
(43, 22, 'c0834cc022b945738196d7d12ac17048_Brown_Jacket_2.png', '2025-11-04 06:28:02'),
(44, 22, 'f1378bca0f364eba877bec604150a149_Brown_Jacket_3.png', '2025-11-04 06:28:02'),
(45, 22, '9fa11ac5dc4b4ddb9d401f616cbc1142_Brown_Jacket.png', '2025-11-04 06:28:02'),
(46, 23, '5efabac0f0bf4d70961c54ea93b72465_Grey_Vest_2.png', '2025-11-04 06:28:30'),
(47, 23, '082be27ad839465ea5761a96ce070c2c_Grey_Vest_3.png', '2025-11-04 06:28:30'),
(48, 23, '96bdc45c128f420a82b5633f791c7cbe_Grey_Vest.png', '2025-11-04 06:28:30'),
(49, 24, '687c790c5b254b86b8635a5311046e9e_Navy_Jacket_1.png', '2025-11-04 06:29:02'),
(50, 24, '99f5efc63fdd47029fb2c75e4e60d8eb_Navy_Jacket_2.png', '2025-11-04 06:29:02'),
(51, 24, '9778ad5b38124329b6d3bae1cd5dcb38_Navy_Jacket_3.png', '2025-11-04 06:29:02'),
(52, 25, 'f8fa0047de3c4de18d02790ef0ac6a57_Grey_Trunks_2.png', '2025-11-04 06:29:52'),
(53, 25, '6d56591174864d04af5430452f183354_Grey_Trunks_3.png', '2025-11-04 06:29:52'),
(54, 25, '5d47aea1d4f547b6b86608ce7797e9c0_Grey_Trunks.png', '2025-11-04 06:29:52'),
(55, 26, '474df0d340b0497b83252bd06a3eda84_Adidas_Samba_2.png', '2025-11-04 06:30:35'),
(56, 26, 'a16f6575a520431c94b03ee871859b2e_Adidas_Samba_3.png', '2025-11-04 06:30:35'),
(57, 26, '22a67cb8370f4046881595d3e4268fc2_Adidas_Samba.png', '2025-11-04 06:30:35'),
(58, 27, '3bef80e8a2094fcbb3545544c94e86bc_Columbia_Wallet_2.png', '2025-11-04 06:31:12'),
(59, 27, 'ba5b2f48f532459b994fa8c60408b3a4_Columbia_Wallet.png', '2025-11-04 06:31:12');

-- --------------------------------------------------------

--
-- Table structure for table `product_variants`
--

CREATE TABLE `product_variants` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `color` varchar(100) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `stock` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `account_type` enum('buyer','seller','rider','admin') NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `region_code` varchar(20) DEFAULT NULL,
  `region_name` varchar(255) DEFAULT NULL,
  `province_code` varchar(20) DEFAULT NULL,
  `province_name` varchar(255) DEFAULT NULL,
  `municipality_code` varchar(20) DEFAULT NULL,
  `municipality_name` varchar(255) DEFAULT NULL,
  `barangay_code` varchar(20) DEFAULT NULL,
  `barangay_name` varchar(255) DEFAULT NULL,
  `street` varchar(255) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `valid_id` varchar(255) DEFAULT NULL,
  `is_google_user` tinyint(1) DEFAULT 0,
  `email_verified` tinyint(1) DEFAULT 0,
  `otp_code` varchar(6) DEFAULT NULL,
  `otp_created_at` datetime DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `store_name` varchar(255) DEFAULT NULL,
  `product_category` varchar(100) DEFAULT NULL,
  `business_permit` varchar(255) DEFAULT NULL,
  `orcr_image` varchar(255) DEFAULT NULL,
  `vehicle_plate_image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `first_name`, `last_name`, `email`, `password`, `account_type`, `phone`, `region_code`, `region_name`, `province_code`, `province_name`, `municipality_code`, `municipality_name`, `barangay_code`, `barangay_name`, `street`, `zip_code`, `valid_id`, `is_google_user`, `email_verified`, `otp_code`, `otp_created_at`, `status`, `created_at`, `updated_at`, `store_name`, `product_category`, `business_permit`, `orcr_image`, `vehicle_plate_image`) VALUES
(1, 'Admin', 'User', 'admin@gmail.com', 'admin123', 'admin', '09123456789', '130000000', 'National Capital Region (NCR)', '137400000', 'Metro Manila', '137404000', 'Quezon City', '137404012', 'Bago Bantay', 'Admin Office Building', '1100', NULL, 0, 1, NULL, NULL, 'approved', '2025-10-31 20:50:11', '2025-10-31 23:31:44', NULL, NULL, NULL, NULL, NULL),
(6, 'Richard', 'Veluz', 'veluz.richard@gmail.com', 'GOOGLE_AUTH', 'seller', '09279114321', '040000000', 'CALABARZON', '043400000', 'Laguna', '043402000', 'Bay', '043402002', 'Calo', 'Arrieta', '4033', '20251104_113431_valid_id.png', 1, 1, NULL, NULL, 'approved', '2025-11-04 03:34:31', '2025-11-04 04:11:39', NULL, NULL, NULL, NULL, NULL),
(7, 'Jamelle', 'Lao', 'jiclao24@gmail.com', 'woewoe123', 'buyer', '09694783874', '040000000', 'CALABARZON', '043400000', 'Laguna', '043419000', 'Pagsanjan', '043419002', 'Biñan', 'DapDap Road', '4033', '20251104_115746_valid_id.png', 0, 1, NULL, NULL, 'approved', '2025-11-04 03:57:46', '2025-11-17 14:01:31', NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_cart_item` (`buyer_id`,`product_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `buyer_id` (`buyer_id`),
  ADD KEY `seller_id` (`seller_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `product_images`
--
ALTER TABLE `product_images`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `product_variants`
--
ALTER TABLE `product_variants`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_region` (`region_code`),
  ADD KEY `idx_province` (`province_code`),
  ADD KEY `idx_municipality` (`municipality_code`),
  ADD KEY `idx_barangay` (`barangay_code`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_wishlist` (`buyer_id`,`product_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `product_images`
--
ALTER TABLE `product_images`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;

--
-- AUTO_INCREMENT for table `product_variants`
--
ALTER TABLE `product_variants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_images`
--
ALTER TABLE `product_images`
  ADD CONSTRAINT `fk_product_images_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_variants`
--
ALTER TABLE `product_variants`
  ADD CONSTRAINT `fk_product_variants_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

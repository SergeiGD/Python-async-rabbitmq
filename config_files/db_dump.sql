--
-- PostgreSQL database dump
--

-- Dumped from database version 12.11 (Ubuntu 12.11-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.11 (Ubuntu 12.11-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;



CREATE TABLE public.books (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    author character varying(50) NOT NULL,
    pages integer NOT NULL
);



CREATE SEQUENCE public.books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.books_id_seq OWNED BY public.books.id;



CREATE TABLE public.users (
    id integer NOT NULL,
    login character varying(50) NOT NULL,
    passwd character varying(65) NOT NULL,
    is_admin boolean NOT NULL
);



CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;



ALTER TABLE ONLY public.books ALTER COLUMN id SET DEFAULT nextval('public.books_id_seq'::regclass);



ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);



COPY public.books (id, name, author, pages) FROM stdin;
\.



COPY public.users (id, login, passwd, is_admin) FROM stdin;
2	user1	e6e07510d6531af5f403d1e6d0eb997855b6453488aaee6a9dd10ad5133f936a	f
3	user2	65e84be33532fb784c48129675f9eff3a682b27168c0ea744b2cf58ee02337c5	f
5	admin	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	t
6	test_user1	e6c3da5b206634d7f3f3586d747ffdb36b5c675757b380c6a5fe5c570c714349	f
7	test_user2	1ba3d16e9881959f8c9a9762854f72c6e6321cdd44358a10a4e939033117eab9	f
8	test_user3	3acb59306ef6e660cf832d1d34c4fba3d88d616f0bb5c2a9e0f82d18ef6fc167	f
9	test_user4	a417b5dc3d06d15d91c6687e27fc1705ebc56b3b2d813abe03066e5643fe4e74	f
10	test_user5	0eeac8171768d0cdef3a20fee6db4362d019c91e10662a6b55186336e1a42778	f
11	test_user6	5c4950c94a3461441c356afa783f76b83b38fd65f730f291403efbcc798acc1f	f
12	test_user7	1526f5e0e31d42fe1c3664ce923ac22ac1333417a90b32043797ac454cd03112	f
13	test_user8	c8fea5b0b76dc690feaf5544749f99b40e78e2a37c0e867a086696509416302a	f
14	test_user9	2d4589473fb3f4581d7452cd25182159d68d2a50056a0cce35a529b010e32f2b	f
15	test_user10	b35892cb8b089e03e4420b94df688122a2b76d4ad0f8b94ad20808bb029e48a5	f
16	test_user11	8057f787ebd8b4f9d40f53d7fbbfcbdde7067c1a074435b68f525b3de0e2ac2b	f
17	test_user12	fdac810d0c09f25c5ddcee9976ab1f1ae1973dba7c65152d95b0937bc2a6c883	f
18	test_user13	1e53de2a2b4ab888cc24002ef8832d433b21956ab83ddeef989c8224b5c8f9f2	f
19	test_user14	b78f24953963ac5ed773d6ec83120e3b1a65510201dc09ed2ed9e9781ba88870	f
20	test_user15	b5a4ec869015095060b1171791334513f741177c4011e2c5c36e3e37a5ff8e5f	f
21	test_user16	f0c28ba3fd9e0dcdcd0470acfcb98cc5a58d7d93422dbbefb930455ef714c87d	f
22	test_user17	4a6b7fa040bcfc734a113fee84d3789c0a626d70d029afad0d1c3e7b6c562e14	f
23	test_user18	b99ddd77e59c96b13b64b3abe1902db4c0a76dabf8622aa6c71f8f5670be6625	f
24	test_user19	871431053023291d24b403f1f9d761c6f01b3050a0a83cd9d9759a970f8d4d92	f
25	test_user20	51d11024031a8951b4722671adfc8587538f5e5417206e7862e60752758a5c35	f
26	test_user21	2d6b3bb57cb9e22fa36516172ef096b30ae00d08eedc1499c599b6269975521d	f
27	test_user22	d0f82756c4d40d20e1fdbc90cf4da4adff02fe23b355687525880514642f764e	f
28	test_user23	8893186d24cce07e1c82f2e020d41177e699318b4be9535483fdf55edf58cd50	f
29	test_user24	cafdc894eacc597ad76db1a750ccb876d4ed69c73b7d3d23f5e3a9e3b5c9fc2e	f
30	test_user25	0028e1c0d2c60966390545414567d33bca9f0165fece6d0109c59a3f29b5fdd0	f
31	test_user26	45e17065ddc6fb3a682f7732df5804652952dbe1f5ca5377a661515a8fcf66be	f
32	test_user27	43b3ec9ea3961a319d37b4cc775d3f43f68709b62a93db10dd6c598137f28732	f
33	test_user28	034a0cdf079dfa3ca924e07e3c509bbf50768d1949b021c0ea0030cff80ba4d1	f
34	test_user29	53f6f072e26d36b9e55d5dc828872856d5286f18ce3818d367f9e4473e464a66	f
35	test_user30	85fcbe6bf830f23209ea6a932921e8da31a653a24a20cb84e75c4997e505690b	f
36	test_user31	3b3ad733c8571384c133694595c33d96c638b36f08a484bd0ad38bf312fdb294	f
37	test_user32	451a8149ebd58dbd064e3337c6de5d4f4bb08cd70bbbd48d62a205bd706b6bb0	f
38	test_user33	0756810289814362efbea8bb826fea0a7bc4318a7f22a4b27b48290cd39951a3	f
39	test_user34	94cd5db06baf087fd56c0042adc1deb162d271acfb8b3eb0277069517998d489	f
40	test_user35	5a66c7ba1398dd71c92a77cc7647c4183e6bf97b227e441bb2674a319b184e63	f
41	test_user36	133f8a05107e5442771c85da3dec70050ae5f3273849326b4a4e2ceaab2ef058	f
42	test_user37	1a31ac086ebf1341c916929e6d982767cd8568887d7c930ba8abd062afa08eac	f
43	test_user38	b64171fda74426604480b9bf7c10ccdc2ebc80266c8667c42346f54ce87d4dec	f
44	test_user39	099646084abbbc2c403c480bea87e7de23ce18db73a3e28251effef3ed49f1ea	f
45	test_user40	d88a53cd8ffe65ab18d2c62882479559aa781642ce7a8d340b22fc0a637b0359	f
46	test_user41	a8a5146b1f97c2c8987ccb3a87d2f30b8aa258c2a32cb96115bf381d42df875c	f
47	test_user42	de3543c757d459090b9adaf9a80a54d54724a0f1600d4c77d6017dde58cf1189	f
48	test_user43	db9aa0719dbf5cac40e44b268042014e9bc28b4134df9051a35f8c64f6603b6f	f
49	test_user44	147eb7dd0f4c59120be8adb20f9dc4d4a0ccb27a0d48d7546dfa171dd980f075	f
50	test_user45	64bf83fcf172a284e3db6b4cc76bb175184ee9dd57e77f0421e3e401ea3858e0	f
51	test_user46	3f1b954c84d8216e09ae793664571dedb1e1bcc9a2bfdc2b6dc58db9a24fa7de	f
52	test_user47	dbb70b94b6b192a1085e8056872daa4eb24002d47c82e88b1323f1a5882567ba	f
53	test_user48	ffe4daf45af0e803fbe1fba2de5c7f7644f30b71ddb082100779d7884e0291c2	f
54	test_user49	a0c69ae7ad7629347d41a89d9a558b26bd9b126a3a183f3498444843acd7270d	f
\.



SELECT pg_catalog.setval('public.books_id_seq', 26714, true);


SELECT pg_catalog.setval('public.users_id_seq', 54, true);



ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);



ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


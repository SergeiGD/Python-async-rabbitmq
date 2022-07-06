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
1	asd	asd	4
3	yyyy	tttt	3
4	kkkk	ttttt	7
6	eewrew	asder	7
\.




COPY public.users (id, login, passwd, is_admin) FROM stdin;
2	user1	e6e07510d6531af5f403d1e6d0eb997855b6453488aaee6a9dd10ad5133f936a	f
3	user2	65e84be33532fb784c48129675f9eff3a682b27168c0ea744b2cf58ee02337c5	f
5	admin	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	t
\.




SELECT pg_catalog.setval('public.books_id_seq', 6, true);




SELECT pg_catalog.setval('public.users_id_seq', 5, true);




ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);




ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);




ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);





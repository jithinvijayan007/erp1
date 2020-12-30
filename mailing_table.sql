--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.19
-- Dumped by pg_dump version 9.5.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: mailing_product; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.mailing_product (
    pk_bint_id bigint NOT NULL,
    vchr_name character varying(100),
    vchr_email character varying(50),
    fk_product_id bigint
);


ALTER TABLE public.mailing_product OWNER TO admin;

--
-- Name: mailing_product_pk_bint_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.mailing_product_pk_bint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mailing_product_pk_bint_id_seq OWNER TO admin;

--
-- Name: mailing_product_pk_bint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.mailing_product_pk_bint_id_seq OWNED BY public.mailing_product.pk_bint_id;


--
-- Name: pk_bint_id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mailing_product ALTER COLUMN pk_bint_id SET DEFAULT nextval('public.mailing_product_pk_bint_id_seq'::regclass);


--
-- Data for Name: mailing_product; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.mailing_product (pk_bint_id, vchr_name, vchr_email, fk_product_id) FROM stdin;
724	SHAMSEER	shamseer@myg.in	6
725	JITHESH	jithesh@myg.in	2
726	JITHESH	jithesh@myg.in	1
727	JITHESH	jithesh@myg.in	7
728	JITHESH	jithesh@myg.in	32
729	JITHESH	jithesh@myg.in	16
730	JITHESH	jithesh@myg.in	33
731	RANITH	ranith@myg.in	14
732	RANITH	ranith@myg.in	5
733	RANITH	ranith@myg.in	21
734	RANITH	ranith@myg.in	9
735	RANITH	ranith@myg.in	10
736	RANITH	ranith@myg.in	17
737	SUJITH	sanoop@myg.in	14
738	SUJITH	sanoop@myg.in	5
739	SUJITH	sanoop@myg.in	21
740	SUJITH	sanoop@myg.in	9
741	SUJITH	sanoop@myg.in	10
742	SUJITH	sanoop@myg.in	17
743	SANOOP	sujith@myg.in	14
744	SANOOP	sujith@myg.in	5
745	SANOOP	sujith@myg.in	21
746	SANOOP	sujith@myg.in	9
747	SANOOP	sujith@myg.in	10
748	SANOOP	sujith@myg.in	17
749	AFSAL	afsalvk@myg.in	15
750	AFSAL	afsalvk@myg.in	18
751	AFSAL	afsalvk@myg.in	11
752	JOHN	john@myg.in	15
753	JOHN	john@myg.in	18
754	KAPIL	kapildev@myg.in	6
755	KAPIL	kapildev@myg.in	14
756	KAPIL	kapildev@myg.in	5
757	KAPIL	kapildev@myg.in	21
758	KAPIL	kapildev@myg.in	9
759	KAPIL	kapildev@myg.in	15
760	KAPIL	kapildev@myg.in	10
761	KAPIL	kapildev@myg.in	17
762	KAPIL	kapildev@myg.in	18
763	KAPIL	kapildev@myg.in	11
764	KAPIL	kapildev@myg.in	25
765	KAPIL	kapildev@myg.in	4
766	KAPIL	kapildev@myg.in	2
767	KAPIL	kapildev@myg.in	1
768	KAPIL	kapildev@myg.in	7
769	KAPIL	kapildev@myg.in	32
770	KAPIL	kapildev@myg.in	16
771	KAPIL	kapildev@myg.in	33
772	SABIK	accounts11@myg.in	6
773	SABIK	accounts11@myg.in	14
774	SABIK	accounts11@myg.in	5
775	SABIK	accounts11@myg.in	21
776	SABIK	accounts11@myg.in	9
777	SABIK	accounts11@myg.in	15
778	SABIK	accounts11@myg.in	10
779	SABIK	accounts11@myg.in	17
780	SABIK	accounts11@myg.in	18
781	SABIK	accounts11@myg.in	11
782	SABIK	accounts11@myg.in	25
783	SABIK	accounts11@myg.in	4
784	SABIK	accounts11@myg.in	2
785	SABIK	accounts11@myg.in	1
786	SABIK	accounts11@myg.in	7
787	SABIK	accounts11@myg.in	32
788	SABIK	accounts11@myg.in	16
789	SABIK	accounts11@myg.in	33
790	SHINE GM	shine@myg.in	6
791	RAJESH NAIR	rajeshnair@mygcare.in	4
792	SHAFI	shafi@mygcare.in	4
793	ARAFATH	arafath@mygsmartchoice.co.in	25
794	SHAMSEER	shamseer@myg.in	\N
795	AJNAS	ajnas@myg.in	\N
796	ANUP	fm@myg.in	\N
797	KAPIL	kapildev@myg.in	\N
798	RAJESH GM	rajesh@myg.in	\N
799	SABIK	accounts11@myg.in	\N
800	SHINE GM	shine@myg.in	\N
\.


--
-- Name: mailing_product_pk_bint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.mailing_product_pk_bint_id_seq', 800, true);


--
-- Name: mailing_product_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mailing_product
    ADD CONSTRAINT mailing_product_pkey PRIMARY KEY (pk_bint_id);


--
-- Name: mailing_product_fk_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mailing_product
    ADD CONSTRAINT mailing_product_fk_product_id_fkey FOREIGN KEY (fk_product_id) REFERENCES public.products(pk_bint_id);


--
-- PostgreSQL database dump complete
--


--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6
-- Dumped by pg_dump version 16.6

-- Started on 2025-12-10 20:31:19

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

--
-- TOC entry 4827 (class 0 OID 32830)
-- Dependencies: 218
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.admins VALUES (17, 608527737, -1002292960714, 'owner');
INSERT INTO public.admins VALUES (20, 6245635972, -1003331706210, 'moderator');
INSERT INTO public.admins VALUES (22, 608527737, -1003331706210, 'owner');


--
-- TOC entry 4825 (class 0 OID 32819)
-- Dependencies: 216
-- Data for Name: channels; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.channels VALUES (11, -1002292960714, 'тестовый канал');
INSERT INTO public.channels VALUES (12, -1003331706210, 'Пробный канал два');


--
-- TOC entry 4833 (class 0 OID 32875)
-- Dependencies: 224
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.posts VALUES (37, -1002292960714, 21, NULL, -1002292960714, 158, 'https://t.me/c/2292960714/158', 'Какие нейросети я использую?', false);
INSERT INTO public.posts VALUES (38, -1002292960714, 21, NULL, -1002292960714, 159, 'https://t.me/c/2292960714/159', 'Стильные иллюстрации в ГПТ', false);
INSERT INTO public.posts VALUES (39, -1002292960714, 21, NULL, -1002292960714, 160, 'https://t.me/c/2292960714/160', 'Отзывы в ГПТ', false);
INSERT INTO public.posts VALUES (40, -1002292960714, 21, 19, -1002292960714, 161, 'https://t.me/c/2292960714/161', 'Автор или ИИ?', false);
INSERT INTO public.posts VALUES (41, -1002292960714, 22, NULL, -1002292960714, 165, 'https://t.me/c/2292960714/165', 'Обо мне и моих каналах', false);
INSERT INTO public.posts VALUES (42, -1002292960714, 22, NULL, -1002292960714, 164, 'https://t.me/c/2292960714/164', 'Канал с отзывами', false);
INSERT INTO public.posts VALUES (43, -1002292960714, 22, NULL, -1002292960714, 163, 'https://t.me/c/2292960714/163', 'Каналы учеников', false);
INSERT INTO public.posts VALUES (16, -1002292960714, 16, NULL, -1002292960714, 137, 'https://t.me/c/2292960714/137', 'Главные ошибки в телеграм', false);
INSERT INTO public.posts VALUES (17, -1002292960714, 16, NULL, -1002292960714, 138, 'https://t.me/c/2292960714/138', 'Обо мне и моих каналах', false);
INSERT INTO public.posts VALUES (18, -1002292960714, 16, NULL, -1002292960714, 139, 'https://t.me/c/2292960714/139', 'формула маркетинга 2025', false);
INSERT INTO public.posts VALUES (19, -1002292960714, 16, NULL, -1002292960714, 140, 'https://t.me/c/2292960714/140', 'Все материалы', false);
INSERT INTO public.posts VALUES (20, -1002292960714, 16, 14, -1002292960714, 141, 'https://t.me/c/2292960714/141', 'Все полезные боты', false);
INSERT INTO public.posts VALUES (21, -1002292960714, 17, NULL, -1002292960714, 142, 'https://t.me/c/2292960714/142', 'Откуда брать идеи постов', false);
INSERT INTO public.posts VALUES (22, -1002292960714, 17, NULL, -1002292960714, 143, 'https://t.me/c/2292960714/143', 'Много идей для постов', false);
INSERT INTO public.posts VALUES (23, -1002292960714, 17, NULL, -1002292960714, 144, 'https://t.me/c/2292960714/144', 'Закрепленный пост', false);
INSERT INTO public.posts VALUES (24, -1002292960714, 17, 15, -1002292960714, 145, 'https://t.me/c/2292960714/145', 'Об этом уже все писали!', false);
INSERT INTO public.posts VALUES (25, -1002292960714, 18, NULL, -1002292960714, 146, 'https://t.me/c/2292960714/146', 'Вы - слишком скучные', false);
INSERT INTO public.posts VALUES (26, -1002292960714, 18, NULL, -1002292960714, 147, 'https://t.me/c/2292960714/147', 'Зачем вам личный бренд', false);
INSERT INTO public.posts VALUES (27, -1002292960714, 18, NULL, -1002292960714, 148, 'https://t.me/c/2292960714/148', 'Вы не собираете отзывы?', false);
INSERT INTO public.posts VALUES (28, -1002292960714, 18, 16, -1002292960714, 149, 'https://t.me/c/2292960714/149', 'Личность не нужна?', false);
INSERT INTO public.posts VALUES (29, -1002292960714, 19, NULL, -1002292960714, 150, 'https://t.me/c/2292960714/150', 'Все способы привлечения', false);
INSERT INTO public.posts VALUES (30, -1002292960714, 19, NULL, -1002292960714, 151, 'https://t.me/c/2292960714/151', 'Куда вести подписчиков?', false);
INSERT INTO public.posts VALUES (31, -1002292960714, 19, NULL, -1002292960714, 152, 'https://t.me/c/2292960714/152', 'Зачем вам канал где 100 подписчиков?', false);
INSERT INTO public.posts VALUES (32, -1002292960714, 19, 17, -1002292960714, 153, 'https://t.me/c/2292960714/153', 'Рекламный креатив', false);
INSERT INTO public.posts VALUES (33, -1002292960714, 20, NULL, -1002292960714, 154, 'https://t.me/c/2292960714/154', 'Бизнес-аккаунт: полезности', false);
INSERT INTO public.posts VALUES (34, -1002292960714, 20, NULL, -1002292960714, 155, 'https://t.me/c/2292960714/155', 'Выдаем лид магнит за подписку', false);
INSERT INTO public.posts VALUES (35, -1002292960714, 20, NULL, -1002292960714, 156, 'https://t.me/c/2292960714/156', 'Как добавить синюю кнопку?', false);
INSERT INTO public.posts VALUES (36, -1002292960714, 20, 18, -1002292960714, 157, 'https://t.me/c/2292960714/157', 'Безопасность в ТГ', false);
INSERT INTO public.posts VALUES (44, -1002292960714, 22, 20, -1002292960714, 162, 'https://t.me/c/2292960714/162', 'Моя лицензия', false);
INSERT INTO public.posts VALUES (45, -1003331706210, 23, NULL, -1003331706210, 34, 'https://t.me/c/3331706210/34', 'Пост 1', false);
INSERT INTO public.posts VALUES (46, -1003331706210, 23, NULL, -1003331706210, 33, 'https://t.me/c/3331706210/33', 'Пост 2', false);
INSERT INTO public.posts VALUES (47, -1003331706210, 23, 21, -1003331706210, 32, 'https://t.me/c/3331706210/32', 'Пост 3', false);
INSERT INTO public.posts VALUES (48, -1003331706210, 24, NULL, -1003331706210, 31, 'https://t.me/c/3331706210/31', 'Пост 1', false);
INSERT INTO public.posts VALUES (49, -1003331706210, 24, NULL, -1003331706210, 30, 'https://t.me/c/3331706210/30', 'Пост 2', false);
INSERT INTO public.posts VALUES (50, -1003331706210, 24, 22, -1003331706210, 29, 'https://t.me/c/3331706210/29', 'Пост 3', false);
INSERT INTO public.posts VALUES (51, -1003331706210, 25, NULL, -1003331706210, 28, 'https://t.me/c/3331706210/28', 'Пост 1', false);
INSERT INTO public.posts VALUES (52, -1003331706210, 25, NULL, -1003331706210, 27, 'https://t.me/c/3331706210/27', 'Пост 2', false);
INSERT INTO public.posts VALUES (53, -1003331706210, 25, 23, -1003331706210, 26, 'https://t.me/c/3331706210/26', 'Пост 3', false);
INSERT INTO public.posts VALUES (54, -1003331706210, 26, NULL, -1003331706210, 25, 'https://t.me/c/3331706210/25', 'Пост 1', false);
INSERT INTO public.posts VALUES (55, -1003331706210, 26, NULL, -1003331706210, 24, 'https://t.me/c/3331706210/24', 'Пост 2', false);
INSERT INTO public.posts VALUES (56, -1003331706210, 26, 24, -1003331706210, 23, 'https://t.me/c/3331706210/23', 'Пост 3', false);
INSERT INTO public.posts VALUES (57, -1003331706210, 27, NULL, -1003331706210, 22, 'https://t.me/c/3331706210/22', 'Пост 1', false);
INSERT INTO public.posts VALUES (58, -1003331706210, 27, NULL, -1003331706210, 21, 'https://t.me/c/3331706210/21', 'Пост 2', false);
INSERT INTO public.posts VALUES (59, -1003331706210, 27, 25, -1003331706210, 20, 'https://t.me/c/3331706210/20', 'Пост 3', false);


--
-- TOC entry 4829 (class 0 OID 32847)
-- Dependencies: 220
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.sections VALUES (16, -1002292960714, 'Важное');
INSERT INTO public.sections VALUES (17, -1002292960714, 'Контент');
INSERT INTO public.sections VALUES (18, -1002292960714, 'Маркетинг и продажи');
INSERT INTO public.sections VALUES (19, -1002292960714, 'Продвижение');
INSERT INTO public.sections VALUES (20, -1002292960714, 'Фишки и лайфхаки');
INSERT INTO public.sections VALUES (21, -1002292960714, 'Нейросети');
INSERT INTO public.sections VALUES (22, -1002292960714, 'Обо мне');
INSERT INTO public.sections VALUES (23, -1003331706210, 'Ремонт ванной');
INSERT INTO public.sections VALUES (24, -1003331706210, 'Ремонт прихожей');
INSERT INTO public.sections VALUES (25, -1003331706210, 'Кухня своими руками');
INSERT INTO public.sections VALUES (26, -1003331706210, 'Дизайн квартиры 37м2');
INSERT INTO public.sections VALUES (27, -1003331706210, 'Дизайн квартиры 51м2');


--
-- TOC entry 4831 (class 0 OID 32861)
-- Dependencies: 222
-- Data for Name: subsections; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.subsections VALUES (14, 16, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (15, 17, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (16, 18, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (17, 19, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (18, 20, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (19, 21, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (20, 22, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (21, 23, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (22, 24, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (23, 25, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (24, 26, 'Подраздел для примера');
INSERT INTO public.subsections VALUES (25, 27, 'Подраздел для примера');


--
-- TOC entry 4844 (class 0 OID 0)
-- Dependencies: 217
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admins_id_seq', 23, true);


--
-- TOC entry 4845 (class 0 OID 0)
-- Dependencies: 215
-- Name: channels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.channels_id_seq', 14, true);


--
-- TOC entry 4846 (class 0 OID 0)
-- Dependencies: 223
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posts_id_seq', 60, true);


--
-- TOC entry 4847 (class 0 OID 0)
-- Dependencies: 219
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sections_id_seq', 29, true);


--
-- TOC entry 4848 (class 0 OID 0)
-- Dependencies: 221
-- Name: subsections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subsections_id_seq', 26, true);


-- Completed on 2025-12-10 20:31:23

--
-- PostgreSQL database dump complete
--


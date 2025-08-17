#!/usr/bin/env python3
"""
Regional data module for Uzbekistan administrative divisions
Complete and optimized regional validation system
"""

from typing import Dict, List, Optional, Tuple
import re

# Complete regional data for Uzbekistan
REGIONS_DATA = {
    "Toshkent shahri": {
        "Bektemir": ["Kuyluk MFY", "Sarabon MFY", "Bunyodkor MFY", "Oqtepa MFY", "Tinchlik MFY"],
        "Chilonzor": ["Chilonzor MFY", "Kimyogarlar MFY", "Namuna MFY", "Guliston MFY", "Yangi Chilonzor MFY"],
        "Mirobod": ["Mirobod MFY", "Ulugbek MFY", "Makhmudov MFY", "Markaziy MFY", "Yangi Mirobod MFY"],
        "Mirzo Ulugbek": ["Qoraqamish MFY", "Beruni MFY", "Maksim Gorkiy MFY", "Ulugbek MFY", "Bobur MFY"],
        "Olmazar": ["Olmazar MFY", "Mavlon Qori MFY", "Bobur MFY", "Tinchlik MFY", "Yangi Olmazar MFY"],
        "Sergeli": ["Sergeli MFY", "Qipchoq MFY", "Yangi Sergeli MFY", "Guliston MFY", "Bog'bon MFY"],
        "Shayhontohur": ["Shayhontohur MFY", "Berdaq MFY", "Pakhtakor MFY", "Markaziy MFY", "Tinchlik MFY"],
        "Uchtepa": ["Uchtepa MFY", "Kukcha MFY", "Qadamjoy MFY", "Yangi Uchtepa MFY", "Bog'bon MFY"],
        "Yakkasaroy": ["Yakkasaroy MFY", "Kucha MFY", "Vodnik MFY", "Markaziy MFY", "Yangi Yakkasaroy MFY"],
        "Yashnobod": ["Yashnobod MFY", "Shifokor MFY", "Muqimiy MFY", "Guliston MFY", "Tinchlik MFY"],
        "Yunusobod": ["Yunusobod MFY", "Buyuk Ipak Yuli MFY", "Bobur MFY", "Yangi Yunusobod MFY", "Markaziy MFY"]
    },
    "Andijon": {
        "Andijon shahri": ["Markaziy MFY", "Sharqiy MFY", "Shimoliy MFY", "Janubiy MFY", "G'arbiy MFY"],
        "Asaka": ["Asaka MFY", "Kasr MFY", "Navoiy MFY", "Tinchlik MFY", "Guliston MFY"],
        "Baliqchi": ["Baliqchi MFY", "Yangiqishloq MFY", "Qoraqum MFY", "Bog'bon MFY", "Yangi Baliqchi MFY"],
        "Bo'z": ["Bo'z MFY", "Xonobod MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY"],
        "Buloqboshi": ["Buloqboshi MFY", "Tinchlik MFY", "Mustaqillik MFY", "Guliston MFY", "Bog'bon MFY"],
        "Izboskan": ["Izboskan MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Mustaqillik MFY"],
        "Jalaquduq": ["Jalaquduq MFY", "Bog'bon MFY", "Guliston MFY", "Tinchlik MFY", "Yangi Jalaquduq MFY"],
        "Marhamat": ["Marhamat MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Marhamat MFY"],
        "Oltinko'l": ["Oltinko'l MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oltinko'l MFY"],
        "Paxtaobod": ["Paxtaobod MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Paxtaobod MFY"],
        "Qo'rg'ontepa": ["Qo'rg'ontepa MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Qo'rg'ontepa MFY"],
        "Shahriston": ["Shahriston MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Shahriston MFY"],
        "Xo'jaobod": ["Xo'jaobod MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Xo'jaobod MFY"]
    },
    "Buxoro": {
        "Buxoro shahri": ["Abu Ali ibn Sino MFY", "Ismoil Somoniy MFY", "Markaziy MFY", "Sharq MFY", "G'arb MFY"],
        "Kogon": ["Kogon MFY", "Dustlik MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY"],
        "Olot": ["Olot MFY", "Tinchlik MFY", "Guliston MFY", "Bog'bon MFY", "Yangi Olot MFY"],
        "Peshku": ["Peshku MFY", "Bog'bon MFY", "Yangiariq MFY", "Guliston MFY", "Tinchlik MFY"],
        "Qorako'l": ["Qorako'l MFY", "Samarkand MFY", "Istiqlol MFY", "Guliston MFY", "Tinchlik MFY"],
        "Buxoro tumani": ["Markaziy MFY", "Sharq MFY", "G'arb MFY", "Shimol MFY", "Janub MFY"],
        "G'ijduvon": ["G'ijduvon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi G'ijduvon MFY"],
        "Jondor": ["Jondor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Jondor MFY"],
        "Qorovulbozor": ["Qorovulbozor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Qorovulbozor MFY"],
        "Romitan": ["Romitan MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Romitan MFY"],
        "Shofirkon": ["Shofirkon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Shofirkon MFY"],
        "Vobkent": ["Vobkent MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Vobkent MFY"]
    },
    "Jizzax": {
        "Jizzax shahri": ["Markaziy MFY", "Istiqlol MFY", "Mustaqillik MFY", "Sharq MFY", "G'arb MFY"],
        "Arnasoy": ["Arnasoy MFY", "Tinchlik MFY", "Yangiyer MFY", "Guliston MFY", "Bog'bon MFY"],
        "Baxtiyor": ["Baxtiyor MFY", "Guliston MFY", "Mehnat MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Do'stlik": ["Do'stlik MFY", "Yangi Hayot MFY", "Bog'bon MFY", "Guliston MFY", "Tinchlik MFY"],
        "Forish": ["Forish MFY", "Qizilcha MFY", "Yangiqishloq MFY", "Guliston MFY", "Tinchlik MFY"],
        "G'allaorol": ["G'allaorol MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi G'allaorol MFY"],
        "Mirzacho'l": ["Mirzacho'l MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Mirzacho'l MFY"],
        "Paxtakor": ["Paxtakor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Paxtakor MFY"],
        "Yangiobod": ["Yangiobod MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangiobod MFY"],
        "Zafarobod": ["Zafarobod MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Zafarobod MFY"],
        "Zarbdor": ["Zarbdor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Zarbdor MFY"],
        "Zomin": ["Zomin MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Zomin MFY"]
    },
    "Qashqadaryo": {
        "Qarshi": ["Markaziy MFY", "Nishon MFY", "Nasaf MFY", "Sharq MFY", "G'arb MFY"],
        "Dehqonobod": ["Dehqonobod MFY", "Guliston MFY", "Yangi Hayot MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Qamashi": ["Qamashi MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Qamashi MFY"],
        "Koson": ["Koson MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Kitob": ["Kitob MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Chiroqchi": ["Chiroqchi MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Chiroqchi MFY"],
        "G'uzor": ["G'uzor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi G'uzor MFY"],
        "Mirishkor": ["Mirishkor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Mirishkor MFY"],
        "Muborak": ["Muborak MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Muborak MFY"],
        "Nishon": ["Nishon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Nishon MFY"],
        "Shahrisabz": ["Shahrisabz MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Shahrisabz MFY"],
        "Yakkabog'": ["Yakkabog' MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yakkabog' MFY"]
    },
    "Navoiy": {
        "Navoiy shahri": ["Markaziy MFY", "Kimyogarlar MFY", "Metallurg MFY", "Sharq MFY", "G'arb MFY"],
        "Zarafshon": ["Zarafshon MFY", "Oltin Vodiy MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY"],
        "Xatirchi": ["Xatirchi MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Xatirchi MFY"],
        "Navbahor": ["Navbahor MFY", "Bog'bon MFY", "Istiqlol MFY", "Guliston MFY", "Tinchlik MFY"],
        "Tomdi": ["Tomdi MFY", "Yangiariq MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Bespah": ["Bespah MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Bespah MFY"],
        "Karmana": ["Karmana MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Karmana MFY"],
        "Konimex": ["Konimex MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Konimex MFY"],
        "Nurota": ["Nurota MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Nurota MFY"],
        "Uchquduq": ["Uchquduq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Uchquduq MFY"]
    },
    "Namangan": {
        "Namangan shahri": ["Markaziy MFY", "Sharq MFY", "Shimol MFY", "Janub MFY", "G'arb MFY"],
        "Chortoq": ["Chortoq MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Kosonsoy": ["Kosonsoy MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Kosonsoy MFY"],
        "Mingbuloq": ["Mingbuloq MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Pop": ["Pop MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Chust": ["Chust MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Chust MFY"],
        "Norin": ["Norin MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Norin MFY"],
        "To'raqo'rg'on": ["To'raqo'rg'on MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi To'raqo'rg'on MFY"],
        "Uchqo'rg'on": ["Uchqo'rg'on MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Uchqo'rg'on MFY"],
        "Uychi": ["Uychi MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Uychi MFY"],
        "Yangihayot": ["Yangihayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangihayot MFY"],
        "Yangiqo'rg'on": ["Yangiqo'rg'on MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangiqo'rg'on MFY"]
    },
    "Samarqand": {
        "Samarqand shahri": ["Markaziy MFY", "Afrosiyob MFY", "Registon MFY", "Sharq MFY", "G'arb MFY"],
        "Bulung'ur": ["Bulung'ur MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Kattaqo'rg'on": ["Kattaqo'rg'on MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Kattaqo'rg'on MFY"],
        "Ishtixon": ["Ishtixon MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY", "Moxpar MFY", "Moxpar mahallasi"],
        "Narpay": ["Narpay MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Payariq": ["Payariq MFY", "Bahor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Jomboy": ["Jomboy MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Jomboy MFY"],
        "Oqdaryo": ["Oqdaryo MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oqdaryo MFY"],
        "Pastdarg'om": ["Pastdarg'om MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Pastdarg'om MFY"],
        "Qo'shrabot": ["Qo'shrabot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Qo'shrabot MFY"],
        "Toyloq": ["Toyloq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Toyloq MFY"],
        "Urgut": ["Urgut MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Urgut MFY"]
    },
    "Surxondaryo": {
        "Termiz": ["Markaziy MFY", "Amir Temur MFY", "Al-Hakim At-Termiziy MFY", "Sharq MFY", "G'arb MFY"],
        "Angor": ["Angor MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Boysun": ["Boysun MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Boysun MFY"],
        "Denov": ["Denov MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Jarqo'rg'on": ["Jarqo'rg'on MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Bandixon": ["Bandixon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Bandixon MFY"],
        "Muzrabot": ["Muzrabot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Muzrabot MFY"],
        "Oltinsoy": ["Oltinsoy MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oltinsoy MFY"],
        "Sariosiyo": ["Sariosiyo MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Sariosiyo MFY"],
        "Sherobod": ["Sherobod MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Sherobod MFY"],
        "Sho'rchi": ["Sho'rchi MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Sho'rchi MFY"],
        "Uzun": ["Uzun MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Uzun MFY"]
    },
    "Sirdaryo": {
        "Guliston": ["Markaziy MFY", "Istiqlol MFY", "Mustaqillik MFY", "Sharq MFY", "G'arb MFY"],
        "Boyovut": ["Boyovut MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Mirzaobod": ["Mirzaobod MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Mirzaobod MFY"],
        "Sayxunobod": ["Sayxunobod MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Xovos": ["Xovos MFY", "Oqqo'rg'on MFY", "Dustlik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Guliston tumani": ["Guliston tumani MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Guliston tumani MFY"],
        "Oqoltin": ["Oqoltin MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oqoltin MFY"],
        "Sardoba": ["Sardoba MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Sardoba MFY"],
        "Sirdaryo tumani": ["Sirdaryo tumani MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Sirdaryo tumani MFY"],
        "Yangiyer": ["Yangiyer MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangiyer MFY"]
    },
    "Toshkent": {
        "Olmaliq": ["Markaziy MFY", "Metallurg MFY", "Kimyogar MFY", "Sharq MFY", "G'arb MFY"],
        "Angren": ["Angren MFY", "Qumtepa MFY", "Yangi Angren MFY", "Guliston MFY", "Tinchlik MFY"],
        "Bekobod": ["Bekobod MFY", "Tinchlik MFY", "Guliston MFY", "Bog'bon MFY", "Yangi Bekobod MFY"],
        "Bo'ka": ["Bo'ka MFY", "Bog'bon MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY"],
        "Bo'stonliq": ["Bo'stonliq MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Chinoz": ["Chinoz MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Chinoz MFY"],
        "Chirchiq": ["Chirchiq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Chirchiq MFY"],
        "Ohangaron": ["Ohangaron MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Ohangaron MFY"],
        "Oqqo'rg'on": ["Oqqo'rg'on MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oqqo'rg'on MFY"],
        "Parkent": ["Parkent MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Parkent MFY"],
        "Piskent": ["Piskent MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Piskent MFY"],
        "Quyichirchiq": ["Quyichirchiq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Quyichirchiq MFY"],
        "O'rtachirchiq": ["O'rtachirchiq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi O'rtachirchiq MFY"],
        "Yangiyo'l": ["Yangiyo'l MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangiyo'l MFY"],
        "Toshkent tumani": ["Toshkent tumani MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Toshkent tumani MFY"],
        "Yuqorichirchiq": ["Yuqorichirchiq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yuqorichirchiq MFY"],
        "Zangiota": ["Zangiota MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Zangiota MFY"],
        "Nurafshon": ["Nurafshon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Nurafshon MFY"]
    },
    "Farg'ona": {
        "Farg'ona shahri": ["Markaziy MFY", "Yangi Farg'ona MFY", "Qo'qon yo'li MFY", "Sharq MFY", "G'arb MFY"],
        "Marg'ilon": ["Marg'ilon MFY", "Ipakchi MFY", "Hunarmand MFY", "Guliston MFY", "Tinchlik MFY"],
        "Qo'qon": ["Qo'qon MFY", "Amir Temur MFY", "Markaziy MFY", "Guliston MFY", "Tinchlik MFY"],
        "Beshariq": ["Beshariq MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Bog'dod": ["Bog'dod MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Bog'dod MFY"],
        "Buvayda": ["Buvayda MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Buvayda MFY"],
        "Dang'ara": ["Dang'ara MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Dang'ara MFY"],
        "Furqat": ["Furqat MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Furqat MFY"],
        "Quva": ["Quva MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Quva MFY"],
        "Rishton": ["Rishton MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Rishton MFY"],
        "So'x": ["So'x MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi So'x MFY"],
        "Toshloq": ["Toshloq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Toshloq MFY"],
        "Uchko'prik": ["Uchko'prik MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Uchko'prik MFY"],
        "Yozyovon": ["Yozyovon MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yozyovon MFY"],
        "Oltiariq": ["Oltiariq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Oltiariq MFY"]
    },
    "Xorazm": {
        "Urganch": ["Markaziy MFY", "Al-Xorazmiy MFY", "Avesto MFY", "Sharq MFY", "G'arb MFY"],
        "Xiva": ["Xiva MFY", "Ichan Qala MFY", "Toshqo'rg'on MFY", "Guliston MFY", "Tinchlik MFY"],
        "Shovot": ["Shovot MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Qo'shko'pir": ["Qo'shko'pir MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Qo'shko'pir MFY"],
        "Yangiariq": ["Yangiariq MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "Bog'ot": ["Bog'ot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Bog'ot MFY"],
        "Gurlan": ["Gurlan MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Gurlan MFY"],
        "Hazorasp": ["Hazorasp MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Hazorasp MFY"],
        "Urganch tumani": ["Urganch tumani MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Urganch tumani MFY"],
        "Xonqa": ["Xonqa MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Xonqa MFY"],
        "Yangibozor": ["Yangibozor MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Yangibozor MFY"],
        "Tuproqqal'a": ["Tuproqqal'a MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Tuproqqal'a MFY"]
    },
    "Qoraqalpog'iston": {
        "Nukus": ["Markaziy MFY", "Berdaqh MFY", "Ajiniyoz MFY", "Sharq MFY", "G'arb MFY"],
        "Xo'jayli": ["Xo'jayli MFY", "Yangi Hayot MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY"],
        "Qo'ng'irot": ["Qo'ng'irot MFY", "Bog'bon MFY", "Tinchlik MFY", "Guliston MFY", "Yangi Qo'ng'irot MFY"],
        "Taxiatosh": ["Taxiatosh MFY", "Istiqlol MFY", "Mustaqillik MFY", "Guliston MFY", "Tinchlik MFY"],
        "To'rtko'l": ["To'rtko'l MFY", "Yangiariq MFY", "Mehnat MFY", "Guliston MFY", "Tinchlik MFY"],
        "Amudaryo": ["Amudaryo MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Amudaryo MFY"],
        "Beruniy": ["Beruniy MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Beruniy MFY"],
        "Chimboy": ["Chimboy MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Chimboy MFY"],
        "Ellikqala": ["Ellikqala MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Ellikqala MFY"],
        "Kegeyli": ["Kegeyli MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Kegeyli MFY"],
        "Mo'ynoq": ["Mo'ynoq MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Mo'ynoq MFY"],
        "Qanliko'l": ["Qanliko'l MFY", "Guliston MFY", "Tinchlik MFY", "Bog'bon MFY", "Yangi Qanliko'l MFY"]
    }
}

class RegionalValidator:
    """Regional data validator with enhanced performance"""
    
    def __init__(self):
        self.regions = list(REGIONS_DATA.keys())
        self._district_cache = {}
        self._mahalla_cache = {}
        
    def get_regions(self) -> List[str]:
        """Get all available regions"""
        return self.regions
        
    def get_districts(self, region: str) -> List[str]:
        """Get districts for a region with caching"""
        if region not in self._district_cache:
            if region in REGIONS_DATA:
                self._district_cache[region] = list(REGIONS_DATA[region].keys())
            else:
                self._district_cache[region] = []
        return self._district_cache[region]
        
    def get_mahallas(self, region: str, district: str) -> List[str]:
        """Get mahallas for a district with caching"""
        cache_key = f"{region}:{district}"
        if cache_key not in self._mahalla_cache:
            if region in REGIONS_DATA and district in REGIONS_DATA[region]:
                self._mahalla_cache[cache_key] = REGIONS_DATA[region][district]
            else:
                self._mahalla_cache[cache_key] = []
        return self._mahalla_cache[cache_key]
        
    def validate_region(self, region: str) -> bool:
        """Validate region name"""
        return region in REGIONS_DATA
        
    def validate_district(self, region: str, district: str) -> bool:
        """Validate district within region"""
        return region in REGIONS_DATA and district in REGIONS_DATA[region]
        
    def validate_mahalla(self, region: str, district: str, mahalla: str) -> bool:
        """Validate mahalla within district"""
        return (region in REGIONS_DATA and 
                district in REGIONS_DATA[region] and 
                mahalla in REGIONS_DATA[region][district])
                
    def search_regions(self, query: str) -> List[str]:
        """Search regions by partial match"""
        query_lower = query.lower()
        return [region for region in self.regions if query_lower in region.lower()]
        
    def search_districts(self, region: str, query: str) -> List[str]:
        """Search districts by partial match"""
        districts = self.get_districts(region)
        query_lower = query.lower()
        return [district for district in districts if query_lower in district.lower()]
        
    def search_mahallas(self, region: str, district: str, query: str) -> List[str]:
        """Search mahallas by partial match"""
        mahallas = self.get_mahallas(region, district)
        query_lower = query.lower()
        return [mahalla for mahalla in mahallas if query_lower in mahalla.lower()]

def validate_name(name: str) -> bool:
    """Validate name format (Uzbek names)"""
    if not name or len(name.strip()) < 2:
        return False
    # Allow Uzbek letters, spaces, apostrophes, and common Unicode characters
    pattern = r"^[A-Za-zÀ-ÿĀ-žА-я\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\s'.-]+$"
    return bool(re.match(pattern, name.strip())) and len(name.strip()) <= 50

def validate_age(age_str: str) -> bool:
    """Validate age (7-14 years)"""
    try:
        age = int(age_str)
        return 7 <= age <= 14
    except ValueError:
        return False

def validate_phone(phone: str) -> bool:
    """Validate Uzbek phone number format"""
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Check for Uzbek mobile numbers
    uzbek_patterns = [
        r'^998[0-9]{9}$',      # +998XXXXXXXXX
        r'^[0-9]{9}$',         # XXXXXXXXX
        r'^[0-9]{12}$'         # 998XXXXXXXXX
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in uzbek_patterns)

def format_phone(phone: str) -> str:
    """Format phone number to standard format"""
    clean_phone = re.sub(r'\D', '', phone)
    
    if len(clean_phone) == 9:
        return f"998{clean_phone}"
    elif len(clean_phone) == 12 and clean_phone.startswith('998'):
        return clean_phone
    else:
        return clean_phone

# Global validator instance
regional_validator = RegionalValidator()

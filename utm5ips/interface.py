#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import sys
from configparser import ConfigParser
from ipaddress import ip_network
import logging
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox
from mysql.connector import MySQLConnection
from utm5ips.__init__ import args


# IP addresses are stored in the database in decimal format
# Some addresses have negative values
# To make them positive it is necessary to add them to the value below
COEFFICIENT: int = 4294967296
# Query for getting ip addresses that are not marked for deletion
SQL_QUERY: str = f"""SELECT INET_NTOA(IF(ip < 0, ip + {COEFFICIENT}, ip))
FROM ip_groups WHERE is_deleted=0"""
# Used in printing results in console mode
TEMPLATE: str = "{}\n------------------\n{}\n"


class Window(QWidget):
    """
    Class for creating QT5 forms with comboboxes
    filled with free addresses in given subnets
    """
    def __init__(self) -> None:
        """ Constructor """

        super().__init__()
        self.setWindowTitle("UTM5 Free IPs")
        self.layout = QFormLayout()

    def fix_size(self) -> None:
        """ Function makes window non-resisable """
        self.setMaximumSize(self.width(), self.height())
        self.setMinimumSize(self.width(), self.height())

    def add_subnet(self, subnet: str, addresses: list[str]) -> None:
        """
        Function fills list of free ip addresses in combobox

        :param subnet: Subnet of free addresses
        :type subnet: str

        :param addresses: List of free addresses of the subnet
        :type addresses: List[str]
        """
        label = QLabel(subnet)
        combobox = QComboBox()
        combobox.addItems(addresses)
        self.layout.addRow(label, combobox)
        self.setLayout(self.layout)


def get_config(filename: str = "config.ini") -> dict:
    """
    Function returns database connection settings

    :param filename: Config filename
    :type filename: str

    :returns: Dictionary with connection settings
    :rtype: Dict[str, {Dict[str], List[str]}]
    """
    config = {
        "database": {
            "host": "",
            "database": "",
            "user": "",
            "password": ""
        },
        "subnets": [],
        "exceptions": []
    }
    parser = ConfigParser()
    if sys.platform.startswith("win32"):
        full_name: str = sys.path[0] + "\\" + filename
    else:
        full_name: str = sys.path[0] + "/" + filename
    try:
        parser.read(full_name)
        items: list[tuple[str]] = parser.items("database")
        for item in items:
            config["database"][item[0]] = item[1]
        for section in ("subnets", "exceptions"):
            items: list[tuple[str]] = parser.items(section)
            for item in items:
                config[section].append({item[0]: item[1]})
        return config
    except Exception as err:
        logging.error("Error in config file or file does not exist.")
        logging.error(err)
    quit()


def connect_to_db() -> MySQLConnection:
    """
    Function connects to a database using parameters
    from config file and returns a connection

    :returns: Reference to an object representing a database connection
    :rtype: MySQLConnection
    """
    db_config = get_config()["database"]
    if db_config:
        try:
            conn = MySQLConnection(**db_config)
            if conn.is_connected():
                return conn
            else:
                logging.error("Could not connect to the database.")
        except Exception as err:
            logging.error("Unable to raise database connection.")
            logging.error(err)
    else:
        logging.error("Could not get database configuration.")
    quit()


def get_ips_from_db() -> list:
    """
    Function returns list of ip addresses from a database

    :returns: Array of ip addresses
    :rtype: List[str]
    """
    ips_from_db: list[str] = []
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)
        db_data = cursor.fetchall()
        if len(db_data) > 0:
            for ip in db_data:
                ips_from_db.append(ip[0])
            conn.close()
            return ips_from_db
        else:
            logging.error("Could not find any address in the database.")
    except Exception as err:
        logging.error("Unable to fetch addresses from database.")
        logging.error(err)
    quit()


def get_free_ips() -> dict:
    """
    Function returns dictionary with free ip addresses

    :returns: Dictionary with ip addresses
    :rtype: Dict[str, List[str]]
    """
    ips_from_db = get_ips_from_db()
    # Key of the dictionary is a subnet address
    # Value is a list of free ip addresses
    # available in the given subnet
    ip_addresses: dict[str, list[str]] = {}
    exceptions: list[str] = []
    config: dict = get_config()
    subnets: dict[str] = config["subnets"]
    for item in config["exceptions"]:
        for key, value in item.items():
            exceptions.append(value)
    if subnets:
        for subnet in subnets:
            items = subnet.items()
            for key, value in items:
                value = ip_network(value)
                ip_addresses[key] = []
                hosts = value.hosts()
                for ip in hosts:
                    ip = str(ip)
                    if ip not in ips_from_db and ip not in exceptions:
                        ip_addresses[key].append(ip)
                        # If -a parameter is not passed, only one free
                        # ip address for each subnet must be added to the list
                        if not args.all:
                            break
        return ip_addresses
    else:
        logging.error("No subnet defined in config file.")
    quit()

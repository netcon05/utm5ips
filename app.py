#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import sys
from PyQt5.QtWidgets import QApplication
from utm5ips.interface import get_free_ips, TEMPLATE, Window
from utm5ips.__init__ import args


def main():
    """Application entry point """
    ip_addresses: list[str] = get_free_ips()
    if args.mode == "con":
        for key, value in ip_addresses.items():
            print(TEMPLATE.format(key, "\n".join(value)))
    else:
        app = QApplication(sys.argv)
        frm_main = Window()
        for key, value in ip_addresses.items():
            frm_main.add_subnet(key, value)
        frm_main.show()
        frm_main.fix_size()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

from flask import Blueprint, flash, Markup, redirect, render_template, url_for

from forms import RegistrationForm
from models import db, query_to_list, Site, Visit
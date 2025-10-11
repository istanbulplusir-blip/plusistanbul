// Fallback jsi18n functions to prevent 503 errors
(function (globals) {
    'use strict';

    const django = globals.django || (globals.django = {});

    // Only add functions if they don't exist
    if (!django.interpolate) {
        django.pluralidx = function (n) {
            const v = (n > 1);
            if (typeof v === 'boolean') {
                return v ? 1 : 0;
            } else {
                return v;
            }
        };

        django.interpolate = function (fmt, obj, named) {
            if (named) {
                return fmt.replace(/%\(\w+\)s/g, function (match) { return String(obj[match.slice(2, -2)]) });
            } else {
                return fmt.replace(/%s/g, function (match) { return String(obj.shift()) });
            }
        };

        django.gettext = function (msgid) {
            return msgid; // Simple fallback
        };

        django.ngettext = function (singular, plural, count) {
            return (count == 1) ? singular : plural;
        };

        django.gettext_noop = function (msgid) { return msgid; };

        django.pgettext = function (context, msgid) {
            return msgid;
        };

        django.npgettext = function (context, singular, plural, count) {
            return (count == 1) ? singular : plural;
        };

        // Formats
        django.formats = {
            "DATETIME_FORMAT": "j F Y، ساعت G:i",
            "DATE_FORMAT": "j F Y",
            "DECIMAL_SEPARATOR": ".",
            "FIRST_DAY_OF_WEEK": 6,
            "MONTH_DAY_FORMAT": "j F",
            "NUMBER_GROUPING": 3,
            "SHORT_DATETIME_FORMAT": "Y/n/j، G:i",
            "SHORT_DATE_FORMAT": "Y/n/j",
            "THOUSAND_SEPARATOR": ",",
            "TIME_FORMAT": "G:i",
            "YEAR_MONTH_FORMAT": "F Y"
        };

        django.get_format = function (format_type) {
            const value = django.formats[format_type];
            if (typeof value === 'undefined') {
                return format_type;
            } else {
                return value;
            }
        };

        console.log('✅ jsi18n fallback functions loaded');
    }

})(this);
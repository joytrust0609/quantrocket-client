# Copyright 2019 QuantRocket - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

def add_subparser(subparsers):
    _parser = subparsers.add_parser("realtime", description="QuantRocket real-time market data CLI", help="Collect and query real-time market data")
    _subparsers = _parser.add_subparsers(title="subcommands", dest="subcommand")
    _subparsers.required = True

    examples = """
Create a new database for collecting real-time tick data.

The market data requirements you specify when you create a new database are
applied each time you collect data for that database.

Examples:

Create a database for collecting real-time trades and volume for US stocks:

    quantrocket realtime create-tick-db usa-stk-trades -u usa-stk --fields last volume

Create a database for collecting trades and quotes for a universe of futures:

    quantrocket realtime create-tick-db globex-fut-taq -u globex-fut --fields last volume bid ask bid_size ask_size
    """
    parser = _subparsers.add_parser(
        "create-tick-db",
        help="create a new database for collecting real-time tick data",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "code",
        metavar="CODE",
        help="the code to assign to the database (lowercase alphanumerics and hyphens only)")
    parser.add_argument(
        "-u", "--universes",
        metavar="UNIVERSE",
        nargs="*",
        help="include these universes")
    parser.add_argument(
        "-i", "--conids",
        metavar="CONID",
        nargs="*",
        help="include these conids")
    parser.add_argument(
        "-v", "--vendor",
        metavar="VENDOR",
        choices=["ib"],
        help="the vendor to collect data from (default 'ib'. Possible choices: "
        "%(choices)s)")
    parser.add_argument(
        "-f", "--fields",
        metavar="FIELD",
        nargs="*",
        help="collect these fields (pass '?' or any invalid fieldname to see "
        "available fields, default fields are 'last' and 'volume')")
    parser.add_argument(
        "-p", "--primary-exchange",
        action="store_true",
        help="limit to data from the primary exchange")
    parser.set_defaults(func="quantrocket.realtime._cli_create_tick_db")

    examples = """
Create an aggregate database from a tick database.

Aggregate databases provide rolled-up views of the underlying tick data,
aggregated to a desired frequency (such as 1-minute bars).

Examples:

Create an aggregate database of 1 minute bars consisting of OHLC trades and volume,
from a tick database of US stocks:

    quantrocket realtime create-agg-db usa-stk-trades-1min --from usa-stk-trades -z 1m --close last volume --open last --high last --low last

Create an aggregate database of 1 second bars containing the last bid and ask and
the mean bid size and ask size, from a tick database of futures trades and
quotes:

    quantrocket realtime create-agg-db globex-fut-taq-1sec --from globex-fut-taq -z 1s --close bid ask --mean bid_size ask_size
    """
    parser = _subparsers.add_parser(
        "create-agg-db",
        help="create an aggregate database from a tick database",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "code",
        metavar="CODE",
        help="the code to assign to the aggregate database (lowercase alphanumerics and hyphens only)")
    parser.add_argument(
        "-f", "--from",
        metavar="CODE",
        required=True,
        dest="from_code",
        help="the code of the tick database to aggregate")
    parser.add_argument(
        "-z", "--bar-size",
        metavar="BAR_SIZE",
        required=True,
        help="the time frequency to aggregate to (use a PostgreSQL interval string, for example "
        "10s or 1m or 2h or 1d)")
    parser.add_argument(
        "-c", "--close",
        metavar="FIELD",
        nargs="*",
        dest="close_fields",
        help="include closing tick for these fields")
    parser.add_argument(
        "-o", "--open",
        metavar="FIELD",
        nargs="*",
        dest="open_fields",
        help="include opening tick for these fields")
    parser.add_argument(
        "-g", "--high",
        metavar="FIELD",
        nargs="*",
        dest="high_fields",
        help="include high tick for these fields")
    parser.add_argument(
        "-l", "--low",
        metavar="FIELD",
        nargs="*",
        dest="low_fields",
        help="include low tick for these fields")
    parser.add_argument(
        "-m", "--mean",
        metavar="FIELD",
        nargs="*",
        dest="mean_fields",
        help="include mean tick for these fields")
    parser.set_defaults(func="quantrocket.realtime._cli_create_agg_db")

    examples = """
Return the configuration for a tick database or aggregate database.

Examples:

Return the configuration for a tick database called "globex-fut-taq":

    quantrocket realtime config 'globex-fut-taq'

Return the configuration for an aggregate database called "globex-fut-taq-1s":

    quantrocket realtime config 'globex-fut-taq-1s'
    """
    parser = _subparsers.add_parser(
        "config",
        help="return the configuration for a tick database or aggregate database",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "code",
        help="the tick database code or aggregate database code")
    parser.set_defaults(func="quantrocket.realtime._cli_get_db_config")

    examples = """
Delete a tick database or aggregate database.

Deleting a tick database deletes its configuration and data and any
associated aggregate databases. Deleting an aggregate database does not
delete the tick database from which it is derived.

Deleting databases is irreversible.

Examples:

Delete a database called "usa-stk-trades":

    quantrocket realtime drop-db 'usa-stk-trades' --confirm-by-typing-db-code-again 'usa-stk-trades'
    """
    parser = _subparsers.add_parser(
        "drop-db",
        help="delete a tick database or aggregate database",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "code",
        help="the tick database code or aggregate database code")
    parser.add_argument(
        "--confirm-by-typing-db-code-again",
        metavar="CODE",
        required=True,
        help="enter the db code again to confirm you want to drop the database, its config, "
        "and all its data")
    parser.add_argument(
        "--cascade",
        action="store_true",
        help="also delete associated aggregated databases, if any. Only applicable when "
       "deleting a tick database.")
    parser.set_defaults(func="quantrocket.realtime._cli_drop_db")

    examples = """
Collect real-time market data and save it to a tick database.

A single snapshot of market data or a continuous stream of market data can
be collected, depending on the `--snapshot` parameter.

Streaming real-time data is collected until cancelled, or can be scheduled
for cancellation using the `--until` parameter.

Examples:

Collect market data for all securities in a database called 'japan-banks-trades':

    quantrocket realtime collect japan-banks-trades

Collect market data for a subset of securities in a database called 'usa-stk-trades'
and automatically cancel the data collection in 30 minutes:

    quantrocket realtime collect usa-stk-trades --conids 12345 23456 34567 --until 30m

Collect a market data snapshot and wait until it completes:

    quantrocket realtime collect usa-stk-trades --snapshot --wait
    """
    parser = _subparsers.add_parser(
        "collect",
        help="collect real-time market data and save it to a tick database",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "codes",
        metavar="CODE",
        nargs="+",
        help="the database code(s) to collect data for")
    parser.add_argument(
        "-i", "--conids",
        nargs="*",
        metavar="CONID",
        help="collect market data for these conids, overriding db config "
        "(typically used to collect a subset of securities)")
    parser.add_argument(
        "-u", "--universes",
        nargs="*",
        metavar="UNIVERSE",
        help="collect market data for these universes, overriding db config "
        "(typically used to collect a subset of securities)")
    parser.add_argument(
        "-f", "--fields",
        nargs="*",
        metavar="FIELD",
        help="limit to these fields, overriding db config")
    parser.add_argument(
        "--until",
        metavar="TIME_OR_TIMEDELTA",
        help="schedule data collection to end at this time. Can be a datetime "
        "(YYYY-MM-DD HH:MM:SS), a time (HH:MM:SS), or a Pandas timedelta "
        "string (e.g. 2h or 30min). If not provided, market data is collected "
        "until cancelled.")
    parser.add_argument(
        "-s", "--snapshot",
        action="store_true",
        help="collect a snapshot of market data (default is to collect a continuous "
        "stream of market data)")
    parser.add_argument(
        "-w", "--wait",
        action="store_true",
        help="wait for market data snapshot to complete before returning (default is "
        "to return immediately). Requires --snapshot")
    parser.set_defaults(func="quantrocket.realtime._cli_collect_market_data")

    examples = """
Return the number of tickers currently being collected, by vendor and database.

Examples:

    quantrocket realtime active
    """
    parser = _subparsers.add_parser(
        "active",
        help="return the number of tickers currently being collected, by vendor and database",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-d", "--detail",
        action="store_true",
        help="return lists of tickers (default is to return counts of tickers)")
    parser.set_defaults(func="quantrocket.realtime._cli_get_active_collections")

    examples = """
Cancel market data collection.

Examples:

Cancel market data collection for a database called 'globex-fut-taq':

    quantrocket realtime cancel 'globex-fut-taq'

Cancel all market data collection:

    quantrocket realtime cancel --all
    """
    parser = _subparsers.add_parser(
        "cancel",
        help="cancel market data collection",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "codes",
        metavar="CODE",
        nargs="*",
        help="the database code(s) to cancel collection for")
    parser.add_argument(
        "-i", "--conids",
        nargs="*",
        metavar="CONID",
        help="cancel market data for these conids, overriding db config")
    parser.add_argument(
        "-u", "--universes",
        nargs="*",
        metavar="UNIVERSE",
        help="cancel market data for these universes, overriding db config")
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        dest="cancel_all",
        help="cancel all market data collection")
    parser.set_defaults(func="quantrocket.realtime._cli_cancel_market_data")

    examples = """
Query market data from a tick database or aggregate database and download to file.

Examples:

Download a CSV of futures market data since 08:00 AM Chicago time:

    quantrocket realtime get globex-fut-taq --start-date '08:00:00 America/Chicago' -o globex_taq.csv
    """
    parser = _subparsers.add_parser(
        "get",
        help="query market data from a tick database or aggregate database and download to file",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "code",
        metavar="CODE",
        help="the code of the tick database or aggregate database to query")
    filters = parser.add_argument_group("filtering options")
    filters.add_argument(
        "-s", "--start-date",
        metavar="YYYY-MM-DD",
        help="limit to market data on or after this datetime. Can pass a date (YYYY-MM-DD), "
        "datetime with optional timezone (YYYY-MM-DD HH:MM:SS TZ), or time with "
        "optional timezone. A time without date will be interpreted as referring to "
        "today if the time is earlier than now, or yesterday if the time is later than "
        "now.")
    filters.add_argument(
        "-e", "--end-date",
        metavar="YYYY-MM-DD",
        help="limit to market data on or before this datetime. Can pass a date (YYYY-MM-DD), "
        "datetime with optional timezone (YYYY-MM-DD HH:MM:SS TZ), or time with "
        "optional timezone.")
    filters.add_argument(
        "-u", "--universes",
        nargs="*",
        metavar="UNIVERSE",
        help="limit to these universes")
    filters.add_argument(
        "-i", "--conids",
        type=int,
        nargs="*",
        metavar="CONID",
        help="limit to these conids")
    filters.add_argument(
        "--exclude-universes",
        nargs="*",
        metavar="UNIVERSE",
        help="exclude these universes")
    filters.add_argument(
        "--exclude-conids",
        type=int,
        nargs="*",
        metavar="CONID",
        help="exclude these conids")
    outputs = parser.add_argument_group("output options")
    outputs.add_argument(
        "-o", "--outfile",
        metavar="OUTFILE",
        dest="filepath_or_buffer",
        help="filename to write the data to (default is stdout)")
    output_format_group = outputs.add_mutually_exclusive_group()
    output_format_group.add_argument(
        "-j", "--json",
        action="store_const",
        const="json",
        dest="output",
        help="format output as JSON (default is CSV)")
    outputs.add_argument(
        "-f", "--fields",
        metavar="FIELD",
        nargs="*",
        help="only return these fields (pass '?' or any invalid fieldname to see "
        "available fields)")
    parser.set_defaults(func="quantrocket.realtime._cli_download_market_data_file")

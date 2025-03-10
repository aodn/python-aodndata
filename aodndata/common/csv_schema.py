"""A Class to validate/type convert CSV files based on a schema."""
import os
import csv
import logging
from schema import And, Schema, SchemaError

logger = logging.getLogger(__name__)

DIALECT_CSV = {"delimiter": ",", "strict": True}


class CSVSchema:
    """A class to validate and/or type convert a CSV file."""

    @staticmethod
    def validate_header(header, cschema):
        """Validate the CSV Headers.

        Args:
          header(list): The CSV header list of str.
          cschema(dict): The schema dictionary.

        Returns:
          Any: the result of schema validation.

        Raises:
          SchemaError: if header is non-conformant.

        """
        expected_keys = list(cschema.keys())
        return Schema(And(list, expected_keys)).validate(header)

    @staticmethod
    def validate_row(datadict, nrow, cschema):
        """Validate a row in a CSV data dictionary with a predefined schema.

        Args:
          datadict(dict): a dictionary.
          nrow(int): a integer row.
          cschema(:obj:`dict,Schema`): A schema dict or a initalized schema class.

        Returns:
          None: if the row is valid.

        Raises:
          SchemaError: if row is non-conformant.

        """
        if str(cschema.__class__) == "dict":
            cschema = Schema(cschema)

        try:
            return cschema.validate(datadict)
        except Exception as e:
            extra_info = "Validation failed at line %s with msg:\n" % nrow
            e.args = tuple("".join([extra_info, *e.args]))
            raise e

    @staticmethod
    def validate_self_content(keypairs, datadict):
        """Validate a dict by comparing keypairs.

        Args:
          keypairs(obj): Iterable of tuples strings with len==2
          datadict(dict): a dict

        Returns:
          None: if all entries are equal.

        Raises:
          SchemaError: if any key pair is different.

        """
        datakeys = set(datadict.keys())
        reqkeys = {y for x in keypairs for y in x}
        missing = not reqkeys.issubset(datakeys)

        if missing:
            errmsg = (
                "Content validation failed.\n\
                    Cannot compare missing keys: %s "
                % (missing)
            )
            raise SchemaError(errmsg)

        for k1, k2 in keypairs:
            v1 = datadict[k1]
            v2 = datadict[k2]
            if v1 != v2:
                errmsg = (
                    "Content validation failed.\n\
                          (d[%s] = %s) != (d[%s] = %s)"
                    % (k1, v1, k2, v2)
                )
                raise SchemaError(errmsg)

    @staticmethod
    def load_csv_header(fname, dialect_csv=None):
        """Load the csv header.

        Args:
          fname(str): File name
          dialect_csv(dict): The csv.reader argument options

        Returns:
          list: A list of strings representing the csv header.

        Raises:
          csv.Error: if invalid csv file.

        """
        if dialect_csv is None:
            dialect_csv = DIALECT_CSV

        with open(fname) as file:
            reader = csv.reader(file, **dialect_csv)
            try:
                return next(reader)
            except StopIteration:
                return []

    @staticmethod
    def load_csv(fname, bulk_load=True, skip_every=0, dialect_csv=None):
        """Load a CSV file.

        This function can load the csv
        file by bulk_loading or by reading row by row
        with skip support.

        Args:
          fname(str): File name
          bulk_load(bool): True for bulkload, False to read row by row
          skip_every(int): read row interval
          dialect_csv(dict): The csv.reader argument options

        Returns:
          list: row_numbers - list of row number read
          dict: header - The header dict
          list: data_rows - list with data rows

        Raises:
          csv.Error: if invalid csv file.

        """
        if dialect_csv is None:
            dialect_csv = DIALECT_CSV

        with open(fname) as file:
            reader = csv.reader(file, **dialect_csv)
            try:
                header = next(reader)
            except StopIteration:
                return range(0), [], []

            if bulk_load:
                data_rows = list(reader)
                row_numbers = range(1, len(data_rows))
                if skip_every:
                    data_rows = data_rows[::skip_every]
                    row_numbers = row_numbers[::skip_every]
            else:
                data_rows = []
                row_numbers = []  # type:ignore
                for nrow, row in enumerate(reader):
                    if skip_every:
                        if nrow % skip_every:
                            data_rows += [row]
                            row_numbers += [nrow]  # type: ignore
                    else:
                        data_rows += [row]
                        row_numbers += [nrow]  # type:ignore
            return row_numbers, header, data_rows

    @staticmethod
    def aggregate_to_dict(headers, data_list):
        """Aggregate all csv rows into a dictionary with header column names as keys and
        values as a list of all row entries.

        Args:
          headers(list): a list of strings for keys
          data_list(list): a list of strings with all data rows

        Returns:
          Dict[str,List[Any]]: A dict with header columns as keys
          Dict[str,List[Any]]: A dict with header columns as keys
          and all respective values in a list.

        """
        adict = {cname: [] for cname in headers}
        for data in data_list:
            for lind, key in enumerate(headers):
                adict[key] += [data[lind]]
        return adict

    def validate_file(self, file):
        """Validate a csv file.

        Args:
          file(str): a csv file

        Returns:
          header(Dict[str,List[Any]]): A dict with header columns converted as keys
          data(Dict[str,List[Any]]): A dict with data columns converted as keys

        """
        logger.info("Validation Started for %s" % file)
        logger.info("\tLoading content schema for %s" % file)

        file_basename = os.path.basename(file)
        schema_name = self.file2schema(file)
        fschema = self.file_schemas[schema_name]

        logger.info("\tLoading data from %s" % file)
        _, header, data_list = self.load_csv(
            file,
            bulk_load=self.bulk_load,
            skip_every=self.skip_every,
            dialect_csv=self.dialect_csv,
        )

        logger.info("\tValidating Header in %s" % file)
        valid_header = self.validate_header(header, fschema)

        logger.info("\tAggregating data rows for validation in %s" % file)
        col_dict = self.aggregate_to_dict(header, data_list)

        logger.info("\tValidating data types in %s" % file)
        valid_dataset = {}
        for key, value in col_dict.items():
            logger.info("\t\t validating %s[%s]" % (file_basename, key))
            try:
                valid_dataset[key] = Schema([fschema[key]]).validate(value)
            except Exception as e:
                #exception = e
                errormsg = fschema[key]._error
                improved_msg = "\t\t\tFile %s, with Header %s contains value %s. Schema failed with msg: %s" % (file_basename,key,value,errormsg)
                e.args = (improved_msg,);
                raise e

            logger.info("\t\t %s[%s] is valid" % (file_basename, key))

        return valid_header, valid_dataset

    def __init__(self, bulk_load=True, skip_every=0, dialect_csv=None):
        """Initialize the CSV schema Class.

        init args:
            bulk_load(boolean): switch to bulk load the entire csv or read by parts.
            skip_every(int): skip N other lines when validating
            dialect_csv(dict): the csv.reader argument options (e.g. delimiter)

        """
        self.bulk_load = bulk_load
        self.skip_every = 0 if skip_every < 0 else skip_every
        self.dialect_csv = DIALECT_CSV if dialect_csv is None else dialect_csv

import csv
from schema import And, SchemaError, Schema

DIALECT_CSV = {'delimiter': ',', 'strict': True}


class CSVSchema(object):

    bulk_load = False
    skip_every = 0
    cross_content_scope = {}
    cross_values = {}

    @staticmethod
    def validate_header(header, cschema):
        expected_keys = list(cschema.keys())
        return Schema(And(list, expected_keys)).validate(header)

    @staticmethod
    def validate_row(datadict, n, cschema):
        """
        Validate a :datadict: dictionary
        lying at row number :n: with schema class :cschema:

        :datadict: a dictionary
        :n: a integer row
        :cschema: An schema dict or a initalized schema class

        :returns: datadict or a new dict - dependent on :cschema: rules.
        """
        if str(cschema.__class__) == 'dict':
            cschema = Schema(cschema)

        try:
            return cschema.validate(datadict)
        except Exception as e:
            extra_info = "Validation failed at line %s with msg:\n" % n
            e.args = tuple([''.join([extra_info, *e.args])])
            raise e

        pass

    @staticmethod
    def validate_self_content(keypairs, datadict):
        """
        Validate a :datadict: dictionary
        by comparing :keypairs:

        :returns: datadict
        """
        datakeys = set(datadict.keys())
        reqkeys = set([y for x in keypairs for y in x])
        missing = not reqkeys.issubset(datakeys)

        if missing:
            errmsg = "Content validation failed.\n\
                    Cannot compare missing keys: %s " % (missing)
            raise SchemaError(errmsg)

        for k1, k2 in keypairs:
            v1 = datadict[k1]
            v2 = datadict[k2]
            if v1 != v2:
                errmsg = 'Content validation failed.\n\
                          (d[%s] = %s) != (d[%s] = %s)' % (k1, v1, k2, v2)
                raise SchemaError(errmsg)

        return datadict

    @staticmethod
    def load_csv_header(fname, dialect=DIALECT_CSV):
        with open(fname) as file:
            reader = csv.DictReader(file, **dialect)
            return reader.fieldnames

    @staticmethod
    def load_csv(fname, dialect=DIALECT_CSV, bulk_load=True, skip_every=0):
        """
        Do the actual heavy lifiting of loading a csv
        file by bulk_loading or by reading row by row
        with skip support.
        """
        with open(fname) as file:
            reader = csv.DictReader(file, **dialect)
            header = reader.fieldnames
            if bulk_load:
                data_rows = list(reader)
                row_numbers = range(1, len(data_rows))
                if skip_every:
                    data_rows = data_rows[::skip_every]
                    row_numbers = row_numbers[::skip_every]
            else:
                data_rows = []
                row_numbers = []
                for rn, row in enumerate(reader):
                    if skip_every:
                        if rn % skip_every:
                            data_rows += [row]
                            row_numbers += [rn]
                    else:
                        data_rows += [row]
                        row_numbers += [rn]
            return row_numbers, header, data_rows

    @staticmethod
    def agg_csv_data(data_list):
        keys = data_list[0].keys()
        agg_dataset = {k: [] for k in keys}
        for datadict in data_list:
            for k, v in datadict.items():
                agg_dataset[k] += [v]
        return agg_dataset

    @staticmethod
    def compute_cross_values(keys, datadict):
        if set(keys).issubset(datadict.keys()):
            cross_values = {x: set() for x in keys}
            [cross_values[x].update(datadict[x]) for x in cross_values.keys()]
        else:
            return {}

    @classmethod
    def report(self, msg):
        print(self.__name__ + ': ' + msg)

    def validate_file(self, file):
        self.report('Validation Started for %s' % file)
        self.report('\tLoading content schema for %s' % file)

        schema_name = self.file2schema(file)
        fschema = self.file_schemas[schema_name]

        self.report('\tLoading data from %s' % file)
        _, header, data_list = self.load_csv(file,
                                             bulk_load=self.bulk_load,
                                             skip_every=self.skip_every)

        self.report('\tValidating Header in %s' % file)
        valid_header = self.validate_header(header, fschema)

        self.report('\tAggregating data rows for validation in %s' % file)
        agg_dataset = self.agg_csv_data(data_list)

        self.report('\tValidating data types in %s' % file)
        valid_dataset = {}
        for k in agg_dataset.keys():
            # TODO validate per column since the fail output can be verbose
            valid_dataset[k] = Schema([fschema[k]]).validate(agg_dataset[k])
            self.report('\t\t %s[%s] is valid' % (file, k))

        if self.same_keys_content:
            self.report('\t\t\tValidating inter columns in %s' % file)
            self.validate_self_content(self.same_keys_content, valid_dataset)

        if self.cross_content_scope and self.cross_values:
            self.report('\t\t\t\tValidating cross columns references in %s' %
                        file)
            for k in self.cross_values.keys():
                isdiff = set(valid_dataset[k]).difference(self.cross_values[k])
                if isdiff:
                    errmsg = 'Cross content comparison failed.\n\
                            %s[%s] = %s\n~\n%s' % (
                        file, k, self.valid_dataset[k], self.cross_values[k])
                    raise SchemaError(errmsg)
        self.report('Validation ended for %s' % file)

        return valid_header, valid_dataset

    def __init__(self, bulk_load=True, skip_every=0):

        self.bulk_load = bulk_load
        self.skip_every = 0 if skip_every < 0 else skip_every


pass

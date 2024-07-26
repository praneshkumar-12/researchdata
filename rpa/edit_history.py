from rpa.models import Edithistory
from datetime import datetime


def record_update(uniqueid, name, updates, db_object):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    old_record_object = db_object.objects.get(uniqueid=uniqueid)
    old_record_dict = {
        field.name: getattr(old_record_object, field.name)
        for field in old_record_object._meta.fields
    }
    modified = compare_dicts(old_record_dict, updates)

    for key, (old_value, new_value) in modified.items():
        new_record = Edithistory(
            uniqueid=old_record_object,
            edit_timestamp=timestamp,
            edited_by=name,
            field_name=key,
            old_value=old_value,
            new_value=new_value,
        )
        print(old_value,type(old_value),new_value,type(new_value))
        new_record.save()


def compare_dicts(old_dict, new_dict):
    d1_keys = set(old_dict.keys())
    d2_keys = set(new_dict.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    modified_dict = {
        o: (old_dict[o], new_dict[o]) for o in shared_keys if str(old_dict[o]) != str(new_dict[o])
    }
    return modified_dict

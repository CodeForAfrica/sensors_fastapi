from db import run_query


def delete_none_values(dic):
    data = dict(dic)
    keys_to_delete = []
    # cannot delete dictionary while running a loop (RuntimeError: dictionary changed size during iteration)
    for key, val in data.items():
        if val is None:
            keys_to_delete.append(key)
    # delete items where value is None
    for key in keys_to_delete:
        del data[key]

    return data


def generate_insert_query(data: dict, table: str):
    keys = data.keys()
    vals = data.values()

    columns = ""
    for key in keys:
        columns += key + ","
    values = ""
    for val in vals:
        if (type(val).__name__) != "str":
            val = str(val)
            values += val + ","
        else:
            values += "'" + val + "',"

    # Remove last comma which will result in an invalid SQL statement
    columns = columns[:-1]
    values = values[:-1]

    insert_query = f"""INSERT INTO {table}({columns}) 
    VALUES({values});
        """
    return insert_query


async def insert_data(stmt):
    res = await run_query(stmt)
    print("Insert data response")
    print(res)
    return

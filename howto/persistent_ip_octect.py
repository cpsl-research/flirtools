import argparse


def convert_from_octet(oct_str: str) -> int:
    octets = oct_str.split(".")
    return sum([int(octet) * 256**(3-i) for i, octet in enumerate(octets)])


def main(args):
    attrs = ["ip", "subnet", "gateway"]
    for attr in attrs:
        if getattr(args, attr) is not None:
            oct_int = convert_from_octet(getattr(args, attr))
            print(f"{attr:9s}: integer for octet {getattr(args, attr):15s} is {oct_int}")
        else:
            print(f"{attr:9s}: no input passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str)
    parser.add_argument("--subnet", default="255.255.255.0", type=str)
    parser.add_argument("--gateway", default="0.0.0.0", type=str)
    args = parser.parse_args()

    main(args)
import master


def main():
    print("start initialize")
    m = master.Master()
    m.setup()
    print("done")
    print("start running")
    m.run()


if __name__ == "__main__":
    main()

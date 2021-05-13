import jacktripcontrol


def main():
    """
    main
    
    calls the main stop command
    """

    jtc = jacktripcontrol.JackTripControl()
    jtc.stop()
    return


if __name__ == '__main__':
    main()
    
    
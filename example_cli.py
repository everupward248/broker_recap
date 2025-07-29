def show_cli_interface():
    """Display the main CLI interface and handle user selections"""
    
    CLI_interface = input('''Welcome to the broker recap tool.
                  1. Clean all broker files in default path.
                  2. Generate invalid emails per broker.
                  3. Run sample validation logic.
                  4. Change settings.
                  5. Test failure scenario.
                  6. Exit.
                  ''')

    if CLI_interface == '1':
        try:
            # clean all broker files in default path
            print('Cleaning all broker files in default path...')
            # if everything passed, then return a success message
            print('All broker files cleaned successfully')
        except Exception as e:
            # if not, then return a failure message
            print('Failed to clean all broker files')
            print(e)
        # Return to main menu regardless of success/failure
        print('\n' + '='*50 + '\n')
        show_cli_interface()
        
    elif CLI_interface == '2':
        try:
            # generate invalid email drafts for all brokers which have errors
            print('Generating invalid email drafts for all brokers which have errors...')
            # if everything passed, then return a success message
            print('Invalid email drafts generated successfully')
        except Exception as e:
            # if not, then return a failure message
            print('Failed to generate invalid email drafts')
            print(e)
        # Return to main menu regardless of success/failure
        print('\n' + '='*50 + '\n')
        show_cli_interface()
        
    elif CLI_interface == '3':
        try:
            # testing purposes
            print('Running sample validation logic...')
            # if everything passed, then return a success message
            print('Sample validation logic passed')
        except Exception as e:
            # if not, then return a failure message
            print('Sample validation logic failed')
            print(e)
        # Return to main menu regardless of success/failure
        print('\n' + '='*50 + '\n')
        show_cli_interface()
        
    elif CLI_interface == '4':
        try:
            # changing default path settings
            print('Changing default path settings...')
            # if everything passed, then return a success message
            print('Settings changed successfully')
        except Exception as e:
            # if not, then return a failure message
            print('Failed to change default path settings')
            print(e)
        # Return to main menu regardless of success/failure
        print('\n' + '='*50 + '\n')
        show_cli_interface()
        
    elif CLI_interface == '5':
        try:
            # intentional failure test
            print('Testing failure scenario...')
            # Force an exception to test error handling
            raise Exception("Failed entry test - This is an intentional failure for testing purposes")
        except Exception as e:
            # if not, then return a failure message
            print('Failed entry test')
            print(e)
        # Return to main menu regardless of success/failure
        print('\n' + '='*50 + '\n')
        show_cli_interface()
        
    elif CLI_interface == '6':
        print('Exiting broker recap tool. Goodbye!')
        return  # Exit the function and program
        
    else:
        # if not, then return a failure message
        print('Invalid input')
        print('Please enter a valid input')
        # Return to main menu after invalid input
        print('\n' + '='*50 + '\n')
        show_cli_interface()

# Start the CLI interface
if __name__ == "__main__":
    show_cli_interface()


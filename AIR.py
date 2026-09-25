#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 09:58:15 2024

@author: slab
"""
import tabulate
from datetime import datetime
import pymysql
db=pymysql.connect(host="localhost",user="root",passwd="12345678",database='airline')
c=db.cursor()
def display_flights():
    c.execute("select * from FLIGHTS")
    g = c.fetchall()
    print(tabulate.tabulate(g,headers=["Flight_ID","Flight_No","Airline","Departure_Airport","Arrival_Airport","Departure_Date","Departure_Time","Arrival_Time","Flight_Duration","Price_PerPassenger","Seats_Available"],tablefmt="fancy_grid"))
def book_flight():
    p = input("Enter passenger name: ")
    q = input("Enter passenger email: ")
    r = int(input("Enter passenger phone number: "))
    s = input("Enter departure location: ")
    k = input("Enter arrival location: ")
    j=input("When do you want to travel?(YYYY-MM-DD): ")

    # Check if departure and arrival airports exist
    c.execute("select Abbreviation from Airport where City = '%s'"%(s))
    departure_airport = c.fetchone()
    c.execute("select Abbreviation from Airport where City = '%s'"%(k))
    arrival_airport = c.fetchone()
    c.execute("select * from FLIGHTS where Departure_Airport = '%s' and Arrival_Airport = '%s' and date(Departure_Date) = '%s'"%(departure_airport[0], arrival_airport[0], j))
    flights = c.fetchall()
    found=0    
    for i in range(len(flights)):
        found=1
        # Display available flights for user to choose
        print("\nAvailable Flights:") 
        flight_options = []
        for m in flights:
            c.execute("select * from FLIGHTS where Flight_No='%s' and Airline='%s' and Departure_Date='%s' and Departure_Time='%s'and Arrival_Time='%s' and Price_PerPassenger=%d"%(m[1], m[2], m[5], m[6], m[7], m[9])) 
            l=c.fetchall()
            print(tabulate.tabulate(l,headers=["Flight_ID","Flight_No","Airline","Departure_Airport","Arrival_Airport","Departure_Date","Departure_Time","Arrival_Time","Duration","Price_PerPassenger","Seats_Available"],tablefmt="fancy_grid"))
            flight_options.append(m)
            while True: 
                chosen_flight_no = input("\nEnter the Flight No of the flight you want to book: ").strip() 
                selected_flight = next((flight for flight in flights if flight[1] == chosen_flight_no), None) 
                if selected_flight: 
                    break 
                else: 
                    print("Invalid Flight No! Please select a valid flight number.")
        # Check if seats are available
        if selected_flight[10] > 0:
            # Insert passenger and booking data
            c.execute("insert into PASSENGERS (Name, Email, Phone_Number) values ('%s', '%s', '%s')"%(p, q, r))
            db.commit()
            c.execute("select Passenger_ID from PASSENGERS order by Passenger_ID DESC LIMIT 1")
            pass_id = c.fetchone()[0]
            # Use lastrowid to get the last inserted Passenger_ID
            c.execute("insert into BOOKINGS (Passenger_ID, Flight_ID, Booking_Date, Booking_Status) values ('%s', '%s', '%s', '%s')"%(pass_id, selected_flight[0], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Confirmed"))
            db.commit()
            # Update seats available
            c.execute("update FLIGHTS set Seats_Available = Seats_Available - 1 where Flight_ID = '%s'"%(selected_flight[0]))
            db.commit()

            print("\nFlight booked successfully!")
        else:
            print("Sorry, no seats available on this flight!")
    if found==0:
        print("No flights found for the given criteria!")
        return
    db.commit()

# Function to display ticket for booked flight
def generate_ticket(booking_id):
    found=0
    # Retrieve booking details using booking_id
    c.execute("SELECT b.Booking_ID, b.Booking_Status, p.Name, p.Email, p.Phone_Number, f.Flight_No, f.Airline, f.Departure_Airport, f.Arrival_Airport, f.Departure_Date, f.Departure_Time, f.Arrival_Time, f.Price_PerPassenger FROM BOOKINGS b JOIN PASSENGERS p ON b.Passenger_ID = p.Passenger_ID JOIN FLIGHTS f ON b.Flight_ID = f.Flight_ID WHERE b.Booking_ID = %s"%(booking_id))
    booking_details = c.fetchall()
    for i in booking_details:
        found=1
        # Extract details from fetched booking
        booking_id = i[0]
        passenger_name = i[2]
        passenger_email = i[3]
        passenger_phone = i[4]
        flight_no = i[5]
        airline = i[6]
        departure_airport = i[7]
        arrival_airport = i[8]
        departure_date = i[9]
        departure_time = i[10]
        arrival_time = i[11]
        price_per_passenger = i[12]

        # Format ticket information
        ticket = [["Booking ID", booking_id],["Passenger Name", passenger_name],["Email", passenger_email],["Phone Number", passenger_phone],["Flight No", flight_no],["Airline", airline],["Departure Airport", departure_airport],["Arrival Airport", arrival_airport],["Departure Date", departure_date],["Departure Time", departure_time],["Arrival Time", arrival_time],["Total Price", price_per_passenger]]

        # Print ticket details
        print("\n" + "*" * 50)
        print("                     FLIGHT TICKET")
        print("*" * 50)
        print(tabulate.tabulate(ticket, headers=["DETAIL", "INFORMATION"], tablefmt="fancy_grid"))
        print("\n" + "*" * 50)
        print("Thank you for booking with us! Have a pleasant journey.")
        print("*" * 50)
    if found==0:
        print("Booking not found!")
# Function to update a booking
def update_booking():
    book_id = int(input("Enter your Booking ID to update: "))
   
    # Check if booking exists
    c.execute("select * from BOOKINGS where Booking_ID = %d"%(book_id))
    booking = c.fetchone()
   
    for i in booking:
        print("1. Update Email")
        print("2. Update Phone Number")
        choice = int(input("What do you want to update: "))
        if choice == 1:
            new_email = input("Enter new email: ")
            c.execute("update PASSENGERS set Email = '%s' where Passenger_ID = %d"%(new_email, booking[1]))
            db.commit()
            print("Email updated successfully!")
            A=input("Do you want to update anything else(y/n):")
            if A=='y':
                continue
            else:
                break
        elif choice == 2:
            new_phone = input("Enter new phone number: ")
            c.execute("update PASSENGERS set Phone_Number = '%s' where Passenger_ID = %d"%(new_phone, booking[1]))
            db.commit()
            print("Phone number updated successfully!")
            A=input("Do you want to update anything else(y/n):")
            if A=='y':
                continue
            else:
                break  
        else:
            print("Invalid choice!")
            continue
    else:
        print("Booking not found!")

# Function to cancel a booking
def cancel_booking():
    book_id = input("Enter your booking ID to cancel: ")

    # Check if booking exists
    c.execute("select * from BOOKINGS where Booking_ID = '%s'"%(book_id))
    booking = c.fetchone()
    found=0
    if booking[4] == 'Cancelled':
        print("Booking is already cancelled.")
        return
    for i in booking:
        found=1
        # Update booking status to 'Cancelled'
        c.execute("update BOOKINGS set Booking_Status = 'Cancelled' where Booking_ID = '%s'"%(book_id))
        # Update seats available
        c.execute("update FLIGHTS set Seats_Available = Seats_Available + 1 where Flight_ID = '%s'"%(booking[2]))
        db.commit()
    print("Booking cancelled successfully!")
    if found==0:
        print("Booking not found!")
        
# MENU DRIVEN PROGRAM
import WELCOME
WELCOME.welcome()
print("\n～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～")
print("                   𝐔𝐒𝐄𝐑 𝐋𝐎𝐆𝐈𝐍 𝐏𝐎𝐑𝐓𝐀𝐋                     ")
print("～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～")
a=input("\nEnter your username:")
b=input("Enter password:")
c.execute("select * from USER where User_ID='%s'"%(a))
n=c.fetchall()
for i in n:
    if b==i[1]:
        print("User logged in!")
        break
else:
    c.execute("insert into USER values('%s','%s')"%(a,b))
    print("User registered and logged in!")
db.commit()
print("\n～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～")
while True:
    print("\n～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～")
    print("                     𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔                               ")
    print("～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～")
    print("\nHere are the list of choices: \n")
    print("1.Display Existing Flights")
    print("2.Book Your Flight")
    print("3.Display Flight Ticket")
    print("4.Update Booking Details")
    print("5.Cancel Your Flight Booking")
    print("6.Exit")
    x=int(input("\nEnter your choice no.: \n"))
    if x==1:
        display_flights()
        f=input("Do you want to continue?(y/n):")
        if f=='y':
            continue
        else:
            break
    elif x==2:
        book_flight()
        f=input("Do you want to continue?(y/n):")
        if f=='y':
            continue
        else:
            break
    elif x==3:
        booking_id = int(input("Enter your Booking ID to generate the ticket: "))
        generate_ticket(booking_id)
        f=input("Do you want to continue?(y/n):")
        if f=='y':
            continue
        else:
            break
    elif x==4:
        update_booking()
        f=input("Do you want to continue?(y/n):")
        if f=='y':
            continue
        else:
            break
    elif x==5:
        cancel_booking()
        f=input("Do you want to continue?(y/n):")
        if f=='y':
            continue
        else:
            break
    elif x==6:
        print("Thank you for using the portal!")
        break
        db.close()
    else:
        print("Invalid choice! Please try again.")
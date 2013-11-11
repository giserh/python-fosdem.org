Feature: 
    Scenario: Create a Talk
        Given PythonFOSDEM is setup
         When I connect with stephane@wirtel.be and "secret"
         When I create a talk "Evy - Distributed Continuous Integrated Server" at http://www.evy.org


                         / Pyrtal /

                 a file fetch application


    ~ What is Pyrtal?

      A sqlite powered, audit function build-in, file fetch proxy.

    ~ How do I use it?

      1. edit the configuration in the flaskr.py file or
         export an PYRTAL_environment variable
         pointing to a configuration __file__.

      2. initialize the database with this command:

         mkdir -p /var/lib/pyrtal
         sqlite3 /var/lib/pyrtal/db < schema.sql

      3. now you can run flaskr:

         ./pyrtal.py
         sudo nginx -s reload

         the application will greet you on
         http://localhost/

    ~ Does it has test unit yet?

         Nup

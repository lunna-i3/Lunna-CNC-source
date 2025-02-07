# Lunna CNC source
# an free and open source ssn copy

# ~> banners and customization (Banners/ & Settings/)

 U can modify the join banner in the Banners page, and create banners for additional commands
 The cnc source from default comes with just a help command banner and join banner
 with the command already attached
 U can modify the command banner in Banners or create another commands in Settings > config.json > commands 
 To create a main banner(banner when u login on the cnc) u can create a .tfx file on Banners/ called "banner"
 To modify the command line banner, create a cmd_line tfx file and reload the cnc

# ~> Super user commands


 reload                 # Reload the cnc assets
 users                  # Show the users options.
 erase                  # To remove attacks(ongoing or on logs)
 set                    # to modify something without going to the server


# ~> Commands that cant be remade:


 ongoing                # cant be remade on the banners part(u can modify it on code if u want) 
 debug                  # cant be remade on the banners part(u can modify it on code if u want)


# ~> funnel.json / attack informations


 {LEN}                  # The len number that was used (Example: 512)
 {GEO}                  # The geolocation/default geolocation will go here (Example: BR)
 {RPS}                  # The requests per second/default requests per second will go here (Example: 100)
 {HOST}                 # The targeted host (Example: 70.70.70.70)
 {PORT}                 # The targeted port (Example: 80)
 {TIME}                 # The attack duration (Example: 20)
 {METHOD}               # The method that was used (Example: HTTP-NODUS)
 {CONCURRENTS}          # The concurrents/default concurrents will go here (Example: 1)


# ~> response type = string


 <&spinner>             # Var to an spinner [- / | \ -] (only used on title)
 <&user.name>           # Returns the current user name
 <&user.uptime>         # Returns how many time user is logged
 <&user.until_expiry>   # Returns How much time the customer have until expiry (Example: 31 days)
 <&user.createdby>      # Returns who created the user account
 <&user.latest.attacks> # returns user's latest attack
 <&cnc.uptime>          # Returns How long the CNC has been online for (Example: 21 days)
 <&cnc.name>            # Returns CNC name set in the Name section of Settings > config.json


# ~> response type = int

 
 <&user.count.active>   # Returns how many active accounts the cnc have
 <&user.count.total>    # Returns how many accounts the cnc have
 <&user.count.expire>   # Returns how many expired accounts the cnc have
 <&user.running>        # Return how many concurrents the user is using
 <&user.boottime>       # Return the max boottime of the user
 <&user.concurrents>    # Return the max concurrents of the user


# ~> utils, response type = ANSI

 <%color.red>           #
 <%color.blue>          #
 <%color.green>         #
 <%color.black>         #
 <%color.white>         #
 <%color.magenta>       #
 <%color.yellow>        #
 <%color.cyan>          #
 <%color.bright.red>    #
 <%color.bright.blue>   #
 <%color.bright.green>  #
 <%color.bright.magenta>#
 <%color.bright.yellow> #
 <%color.bright.cyan>   #
 <%color.dark.red>      #
 <%color.dark.blue>     #
 <%color.dark.green>    #
 <%color.dark.magenta>  #
 <%color.dark.yellow>   #
 <%color.dark.cyan>     #
 <%color.bg.red>        #
 <%color.bg.blue>       #
 <%color.bg.green>      #
 <%color.bg.black>      #
 <%color.bg.white>      #
 <%color.bg.magenta>    #
 <%color.bg.yellow>     #
 <%color.bg.cyan>       #
 <%color.reset>         #
 <%clear>               # Clear the entire screen.
 
 :> u can also use &x1b or /x1b(escape byte) to put whatever color u want, honey


# ~> security level for your accounts (Settings > configs.json > security_level)


 0                      # No captcha.
 1                      # Math captcha.
 2                      # ASCII text captcha.
 3                      # ASCII image captcha.
 4                      # 2fa via OTP.

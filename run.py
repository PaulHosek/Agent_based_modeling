from server import server
import profile

server.port = 8521 # The default
profile.run(server.launch())


import pygame, time, random

# Define classes / functions
class Construct:
    def __init__(self,size,x=0,y=0):
        self.x = x
        self.y = y
        self.size=size
        self.rect=pygame.Rect(self.x,self.y,self.size[0],self.size[1])
        
    

class Entity(Construct):
    def __init__(self, size, x, y):
        super().__init__(size,x,y) # init attributes from parent class construct
        self.bullets=[] 

    def render(self,screen):
        self.imagesize = self.image.get_size()
        # pygame.draw.rect(screen, (255,255,255), self.rect) # old render method
        screen.blit(pygame.transform.scale(self.image,(int(self.imagesize[0]/3), int(self.imagesize[1]/3))),self.rect)

    def move(self, vel_x, vel_y,vel_inverse): # movement method
        self.x += vel_x*vel_inverse # vel_inverse changes the direction
        self.y += vel_y*vel_inverse # 
        self.rect=pygame.Rect(self.x,self.y,self.size[0],self.size[1]) #update rect attribute with new one when moved

    def getxy(self):
        return(self.x,self.y) #returns position as a tuple
    

#enemy class
class Enemy(Entity):
    def __init__(self, size, x=0, y=0):
        super().__init__(size, x, y) # init attributes from parent class construct 
        self.image = pygame.image.load("enemy.png")
    def shoot(self):
        self.bullets.append(Bullet(self.x+(self.size[0]/2), self.y,1))
    

#player class
class Player(Entity):
    def __init__(self, size, x, y):
        self.image = pygame.image.load("player.png")
        super().__init__(size, x, y)
    
    def shoot(self):
        self.bullets.append(Bullet(self.x+(self.size[0]/2), self.y, -1))

class Bullet(Entity):
    def __init__(self, x, y, downwards):
        self.image = pygame.image.load("bullet.png")
        super().__init__([3,7],x-1.5,y)
        self.downwards=downwards


class Shield(Construct):
    def __init__(self, x, y):
        super().__init__([35,15],x,y)
        self.__damageBlocks=[]

    def damage(self,x,y):
        self.__damageBlocks.append(Damage(x,y))
    
    #render method for shield 
    def render(self,screen):
        pygame.draw.rect(screen, (255,255,255), self.rect)    # old rectangle draw 
        #renders the black damage rects over the shield
        for damage in self.__damageBlocks:
            pygame.draw.rect(screen, (0,0,0), damage.rect)
    
    def testBulletCollision(self, bullet, destructive):
        damaged_area=False
        for damage in self.__damageBlocks:
            #checks for if the bullet is in any of the damaged areas in the shield
            if pygame.Rect.colliderect(damage.top_hitbox,bullet.rect):
                damaged_area=True
        #if the bullet is not in a damaged area, 
        if pygame.Rect.colliderect(self.rect,bullet.rect) and not damaged_area:
            #find the xy of the bullet
            xy=bullet.getxy()    # returns tuple
            if destructive:
                self.damage(xy[0],xy[1]) # create damage at the x and y of the bullet
            return True # returns that it did collide
        

class Damage(Construct):
    def __init__(self,x,y):
        super().__init__([5,random.randint(7,9)], x, y)
        #creates attributes that shows what the top hitbox is for the rect (I couldnt figure out how to get it to test the top of the rect)
        self.top_hitbox=pygame.Rect(self.x,self.y,self.size[0],1)

    

#pygame initialisation
pygame.init()
screen = pygame.display.set_mode([224,256])

clock = pygame.time.Clock()
running = True

#spritesheet init

#spawning enemies
enemyObjs=[]
for x in range(0,10):
    for y in range(0,5):
        enemyObjs.append(Enemy([10,5], x*15+20, y*10+25))


#spawning shields
shields=[]
for x in range(0,3):
    shields.append(Shield((screen.get_width())/3*x+20,165))
prev_time=time.time()
dt=0

#initialise event for moving Enemy
movement_clock=pygame.NUMEVENTS-1

#timer for moving enemy
time_elapsed=0

#timer for shooting
shoot_cooldown=0

#count for how many times the aliens hit the wall
count=0

# -1 = going left  1 = going right
vel_inverse=1

player=Player( [20,7.5] , 20, 200)

enemy_shoot_cd=500

lives=3

# SOUNDS

pygame.mixer.init()

sounds={"shoot" : pygame.mixer.Sound("shoot.wav"),
        "invader_death" : pygame.mixer.Sound("invaderkilled.wav"),
        "invader_move" : pygame.mixer.Sound("fastinvader1.wav"),
        "player_death" : pygame.mixer.Sound("explosion.wav")}
#main loop, running state
while running: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running == False
    
    screen.fill(0)
    # DO GAME LOGIC
    fps=pygame.time.Clock.get_fps(clock)
    now=time.time()
    dt=now-prev_time
    prev_time=now
    time_elapsed+=dt*1000 #dt in ms

    #player input
    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.getxy()[0]>5:
        player.move(2, 0, -1)
    elif keys[pygame.K_RIGHT] and player.getxy()[0]<screen.get_width()-25:
        player.move(2 ,0, 1)
    if keys[pygame.K_SPACE]:
        #if user wants to shoot, check if cooldwon is over
        if now-shoot_cooldown>0.4: #figures out when the last bullet was shot versus the time now
            shoot_cooldown=now
            player.shoot()
            pygame.mixer.Sound.play(sounds["shoot"])

    #move bullets
    for bullet in player.bullets:
        bullet.move(0,5,bullet.downwards)
        
        bullet.render(screen)
    
    for mob in enemyObjs:
        for bullet in mob.bullets:
            bullet.move(0,5,bullet.downwards)
            bullet.render(screen)
#            pygame.mixer.Sound.play(sounds["invader_move"])  // commented because it sounds horrible


    if time_elapsed<enemy_shoot_cd+25 and time_elapsed>enemy_shoot_cd-25:
        #1-2 enemies shoot
        for x in range(0,random.randint(0,1)):
            #create bullet obj using shoot method
            enemyObjs[random.randint(0,len(enemyObjs)-1)].shoot()
            pygame.mixer.Sound.play(sounds["shoot"])
        #randomizes shoot cooldown
        enemy_shoot_cd=random.randint(0,1250)
    
    if time_elapsed>1250:
        #in ms
        #checks to move down    
        if enemyObjs[-1].getxy()[0]>screen.get_width()-30:
            vel_inverse=-1
            count+=1
        
        elif enemyObjs[0].getxy()[0]<30:
            vel_inverse=1
            count+=1
        
        if count==4:
            for mob in enemyObjs:
                mob.move(0,15,1)
            count=0
        else:
            for mob in enemyObjs:
                mob.move(10,0,vel_inverse)
        time_elapsed=0


    for mob in enemyObjs:
        #mob bullet collisions
        for bullet in player.bullets:
            if pygame.Rect.colliderect(mob.rect,bullet.rect):
                #if collision of enemy and bullet, remove from list / kill:
                player.bullets.pop(player.bullets.index(bullet))
                enemyObjs.pop(enemyObjs.index(mob))
                pygame.mixer.Sound.play(sounds["invader_death"])

            #tests each shield to see if it would collide
            for shield in shields:
                if shield.testBulletCollision(bullet,False):
                    #remove bullet if it collides
                    player.bullets.pop(player.bullets.index(bullet))
        
        for bullet in mob.bullets:
            for shield in shields:
                if shield.testBulletCollision(bullet,True):
                    mob.bullets.pop(mob.bullets.index(bullet))


            if pygame.Rect.colliderect(bullet.rect,player.rect):
                lives-=1
                mob.bullets.pop(mob.bullets.index(bullet))
        mob.render(screen)
    
    #render shields and it's damage
    for shield in shields:
        shield.render(screen)
    player.render(screen)
    pygame.display.flip()
    clock.tick(60)
    if lives<=0 or enemyObjs[-1].y>165:
        pygame.mixer.Sound.play(sounds["player_death"])
        #lost game, stop running state
        running=False

#end state
endScreen=True
while endScreen:
    pass
pygame.quit()

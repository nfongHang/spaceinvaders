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
        super().__init__(size,x,y)

    def render(self):
        pygame.draw.rect(screen, (255,255,255), self.rect)

    def move(self, vel_x, vel_y,vel_inverse):
        self.x += vel_x*vel_inverse
        self.y += vel_y*vel_inverse
        self.rect=pygame.Rect(self.x,self.y,self.size[0],self.size[1])

    def getxy(self):
        return[self.x,self.y]
    

#enemy class
class Enemy(Entity):
    def __init__(self, size, x=0, y=0):
        super().__init__(size, x,y)
        self.bullets=[]

    def shoot(self):
        self.bullets.append(Bullet(self.x+(self.size[0]/2), self.y,1))
    

#player class
class Player(Entity):
    def __init__(self, size, x, y):
        super().__init__(size, x, y)
        self.bullets=[]
    
    def shoot(self):
        self.bullets.append(Bullet(self.x+(self.size[0]/2), self.y, -1))

class Bullet(Entity):
    def __init__(self, x, y, downwards):
        super().__init__([3,7],x-1.5,y)
        self.downwards=downwards


class Shield(Construct):
    def __init__(self, x, y):
        super().__init__([35,15],x,y)
        self.__damageBlocks=[]

    def damage(self,x,y):
        self.__damageBlocks.append(Damage(x,y))

    def render(self):
        pygame.draw.rect(screen, (255,255,255), self.rect)
        for damage in self.__damageBlocks:
            pygame.draw.rect(screen, (0,0,0), damage.rect)
    def __getDamage(self):
        return self.__damageBlocks
    def testBulletCollision(self,bullet):
        damaged_area=False
        for damage in self.__getDamage():
            #checks for if the bullet is in any of the damaged areas in the shield
            if pygame.Rect.colliderect(damage.top_hitbox,bullet.rect):
                damaged_area=True
        #if the bullet is not in a damaged area:
        if pygame.Rect.colliderect(self.rect,bullet.rect) and not damaged_area:
            xy=bullet.getxy()
            self.damage(xy[0],xy[1])
            return True
class Damage(Construct):
    def __init__(self,x,y):
        super().__init__([random.randint(5,7),random.randint(6,8)], x, y)
        self.top_hitbox=pygame.Rect(self.x,self.y,self.size[0],1)

    


pygame.init()

screen = pygame.display.set_mode([224,256],pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

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

count=0
vel_inverse=True

player=Player( [30,10] , 20, 200)

enemy_shoot_cd=500

lives=3

#main loop
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
    if keys[pygame.K_LEFT] and player.getxy()[0]>20:
        player.move(2, 0, -1)
    elif keys[pygame.K_RIGHT] and player.getxy()[0]<screen.get_width()-50:
        player.move(2 ,0, 1)
    if keys[pygame.K_SPACE]:

        if now-shoot_cooldown>0.4:
            shoot_cooldown=now
            player.shoot()

    #move bullets
    for bullet in player.bullets:
        bullet.move(0,5,bullet.downwards)
        
        bullet.render()
    
    for mob in enemyObjs:
        for bullet in mob.bullets:
            bullet.move(0,5,bullet.downwards)
            bullet.render()


    if time_elapsed<enemy_shoot_cd+25 and time_elapsed>enemy_shoot_cd-25:
        #1-2 enemies shoot
        for x in range(0,random.randint(0,1)):
            #create bullet obj using shoot method
            enemyObjs[random.randint(0,len(enemyObjs)-1)].shoot()
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
                #if collision of enemy and bullet:
                player.bullets.pop(player.bullets.index(bullet))
                enemyObjs.pop(enemyObjs.index(mob))

            #tests each shield to see if it would collide
            for shield in shields:
                if shield.testBulletCollision(bullet):
                    player.bullets.pop(player.bullets.index(bullet))
        

        for bullet in mob.bullets:
            for shield in shields:
                if shield.testBulletCollision(bullet):
                    mob.bullets.pop(mob.bullets.index(bullet))


            if pygame.Rect.colliderect(bullet.rect,player.rect):
                lives-=1
                mob.bullets.pop(mob.bullets.index(bullet))
        mob.render()
    
    #render shields and it's damage
    for shield in shields:
        shield.render()
    player.render()
    pygame.display.flip()
    clock.tick(60)
    if lives<=0:
        running=False
pygame.quit()

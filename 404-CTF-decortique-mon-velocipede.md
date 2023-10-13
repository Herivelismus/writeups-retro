# 404CTF WRITEUP
Lien : https://github.com/HackademINT/404CTF-2023/tree/main/RetroIngenierie/decortique-mon-velocipede
## Étape 1: Comprendre le set d'instructions

Pour comprendre le set d'instructions virtuelles, nous avons ouvert notre exécutable dans un désassembleur, en utilisant IDA.

Dans la fonction `entry`, on suit le programme et on repére une adresse intéressante à `0x1440`. Le mode graphique d'IDA suggère clairement que cette fonction est l'équivalent d'une instruction `switch` en C. Pour chaque code, une fonction unique est appelée, constituant ainsi notre ensemble d'instructions virtuelles.

#### Cas 0x28 :
Si l'instruction est `0x28`, alors `FUN_001019cf()` est appelée. Ensuite, quelques opérations sont effectuées, de la mémoire est allouée, puis `FUN_0010208c()` est appelée.

Cette fonction recherche l'octet `0x01`, puis récupère n octets suivant pour les comparer à une chaîne de caractères donnée en entrée. Si ces deux chaînes sont égales et que le caractère `0x02` suit, le registre `rsp_virtuelle`, en réalité une adresse dans la pile, est incrémenté.

En ouvrant le fichier .vmr, nous avons observé que le fichier commence par `main |`, qui en représentation ASCII est `01 04 6D 61 69 6E 02`, confirmant ainsi notre analyse.

Les autres fonctions telles que `push` et `pop` fonctionnent de manière similaire en effectuant des opérations avec les registres virtuels.

Voici un récapitulatif partiel du set d'instructions virtuelles :

| Virtuelle  | Réelle    |      | Virtuelle  | Réelle    |
|:----------|:----------|:-----|:----------|:----------|
| 0x21      | jump      |      | 0x2f      | fopen     |
| 0x23      | mov_const |      | 0x3a      | mov       | 
| 0x24      | puts      |      | 0x3c      | pop       |
| 0x25      | getline   |      | 0x3xe     | push      |
| 0x26      | and       |      | 0x2b      | add       |
| 0x28      | call      |      | 0x2d      | sub       | 
| 0x29      | ret       |      | 0x2e      | exit      |
| 0x7c      | push_n_bytes|   | 0x5e      | xor       |


Après une analyse similaire à celle de `call` on comprend que `push_n_bytes` prend en entrée une adresse et un entier `n` et va push n octects à partir de cette adresse.


Si on s'intéresse au code assembleur virtuelle maintenant qu'on peut le comprendre on voit que 176 octects vont être push, en effet on peut lire:

`7C B0 00 00 00 63 3D 21 11 ...`


## Etape 2: récupérer du code assembleur
Après ce push il reste des instructions.
Deux possibilités s'offrent à nous, soit créer un script python pour désassembler notre code d'instruction virtuelle à l'aide d'une pile, soit tricher au débuggeur pour comprendre ce qui ce passe; ou alors faire un peu des deux.

@luca à fait un excellent travail et son programme nous renvoie:

```
226 : 0x5e 0x45 0x45 : xorl $4, $4
229 : 0x23 0x41 0x2c : movc $0, #44
233 : 0x3a 0x42 0x53 : mov $1, $7
236 : 0x3a 0x53 0x44 : mov $7, $3
239 : 0x2b 0x53 0x45 : add $7, $4
242 : 0x3c 0x43      : pop $2
244 : 0x3a 0x53 0x42 : mov $7, $1
247 : 0x3c 0x42      : pop $1
249 : 0x5e 0x42 0x43 : xorl $1, $2
252 : 0x3e 0x42      : push $1 ()
254 : 0x23 0x46 0x4  : movc $5, #4
258 : 0x2b 0x53 0x46 : add $7, $5
261 : 0x2b 0x45 0x46 : add $4, $5
264 : 0x26 0x45 0x46 : andl $4, $5
267 : 0x23 0x46 0x1  : movc $5, #1
271 : 0x2d 0x41 0x46 : sub $0, $5
274 : 0x21 -0x2e     : jnz($0) 229
275 : 0x23 0x46 0x0  : movc $5, #0
279 : 0x2d 0x53 0x46 : sub $7, $5
282 : 0x28 0x9       : call check_key
```
ce qui correspond à l'algorithme suivant:
```
i <- 0
adresse1
adresse2
Tant que i<44:
	x <- prendre 4 octets à partir de adresse1
	y <- pop 4 octets à partir de adresse2
	r <- x xor y
	push r
	adresse2 <- adresse2 + offset de 4
	adresse1 <- adresse2 + offset de (4 % 8) // car le and joue le rôle de modulo
	i <- i + 1
Fin
Appeler check_key  	
```

Tout laisse penser qu'une adresse correspond au mot de passe `mdp` et l'autre au 176 octets que l'on appelle `buffer`.

Or evidemment que tout le `buffer` va être utile donc on va possiblement boucler sur les 8 premiers caractères de `mdp`.

Allons à la fonction `xor` virtuelle et ajoutons un breakpoint juste avant le l'instruction réelle xor qui va comparer le registre `eax` au registre `edx`
On rentre **aaaabbbbcccc** en mot de passe:

On a **eax = 0x61616161** ce qui correspond en ASCII à **aaaa** et **edx = 11213D63** ce qui correspond aux 4 premiers octets push. (en little-endian c'est à l'envers)

A la deuxième boucle on a **eax = 0x62626262** ce qui correspond à **bbbb**

Et à la troisième boucle on a de nouveau **eax = 0x61616161** ! Hypothèse validée; seuls les 8 premiers caractères du mot de passe comptent.

Le flag ne va pas faire 8 caractères donc notre `buffer` est un fait chiffré en quelque sorte et on va le déchiffrer à coups de xor avec le bon mot de passe. Ce `buffer` une fois déchiffré va être executé par la fonction `check_key`, et notre flag sera sûrement affiché.

## Etape 3: Trouver le mot de passe
On va se servir de la propiété suivant dans N: **a ^ b = x ⇔ a = x ^ b**

Si on met n'importe quoi comme mot de passe le programme nous renvoie une erreur en nous disant qu'il n'a pas réussi à appelé `check_key`, or `check_key` cherche le caractère `0x01` puis `0x09` car "check_key" contient neuf caractères puis  `63 68 65 63 6B 5F 6B 65 79`, sa représentation ASCII.

On veut donc générer le chaine de caractère `01 09 63 68 65 63 6B 5F`

On cherche donc x et y tel que `x ^ 0x633D2111 = 0x01096368` et `y ^ 0x22521933 = 0x65636B5F`
ce qui nous donne x = `0x62344279` et y = `0x4731726c`.

En concatenant les representations ASCII de x et y on trouve **B4byG1rl**, le mot de passe est accepté et un flag s'affiche à l'écran.

 

# Sloth Fuzzer - Configuration README

## Description

Ce projet utilise Sloth, un fuzzer basé sur QEMU et LibFuzzer, pour tester des bibliothèques natives Android. La configuration actuelle automatise complètement le processus de compilation et d'exécution du fuzzer sur une bibliothèque vulnérable d'exemple.

## Prérequis

- Docker installé et en cours d'exécution
- Clone du repository Sloth modifié (avec rootfs d'un appareil Android rooté)

## Architecture du projet

```
Sloth/
├── src/
│   ├── fuzz_runner.py      # Script d'automatisation principal
│   ├── fuzzer/             # LibFuzzer
│   ├── qemu/               # QEMU modifié
│   ├── sloth.c             # Code source de Sloth
│   └── test/               # Corpus de test généré automatiquement
├── resources/
│   ├── rootfs/             # Système de fichiers Android
│   └── examples/
│       └── Skia/
│           ├── jni/        # Code source de la bibliothèque cible
│           │   ├── lib/fuzz.cpp    # Fonction vulnérable à fuzzer
│           │   ├── Android.mk
│           │   └── Application.mk
│           └── libs/       # Bibliothèques compilées
└── crashes/                # Dossier des crashes trouvés
```

## Installation et exécution

### 1. Démarrer l'environnement Docker

```bash
cd Sloth/
./run.sh
```
**⚠️ Important:** Assurez-vous que Docker est en cours d'exécution avant de lancer cette commande.

### 2. Lancer le fuzzer automatisé

Une fois dans le conteneur Docker :

```bash
cd /sloth/src/
python3 fuzz_runner.py
```

## Ce que fait le script `fuzz_runner.py`

Le script automatise complètement le processus de fuzzing. Voici le détail de son fonctionnement :

### Configuration par défaut

```python
SLOTH_BIN = "./sloth"                           # Binaire Sloth
TARGET_BIN = "/rootfs/boofuzz"                  # Binaire cible
TARGET_LIB = "/rootfs/system/lib64/libBooFuzz.so"  # Bibliothèque à fuzzer
INPUT_DIR = "./test"                            # Dossier des inputs
CRASH_DIR = "./crashes"                         # Dossier des crashes
NB_CASES = 10                                   # Nombre de cas de test
MAX_INPUT_SIZE = 64                             # Taille max des inputs
```

### Étapes d'exécution

#### 1. Vérification et compilation de Sloth (`ensure_sloth_compiled()`)
- Vérifie si l'exécutable `sloth` existe
- S'il n'existe pas, lance `make` pour compiler :
  - QEMU avec les patches nécessaires
  - LibFuzzer
  - Sloth en liant le tout

#### 2. Génération du corpus de test (`generate_inputs()`)
- Crée le dossier `./test/` s'il n'existe pas
- Génère 10 fichiers d'entrée aléatoires
- Chaque fichier a une taille aléatoire entre 6 et 64 bytes

#### 3. Lancement du fuzzing (`launch_fuzzer()`)
- Configure la variable d'environnement `SLOTH_TARGET_LIBRARY`
- Exécute : `./sloth /rootfs/boofuzz ./test`
- Affiche le progrès en temps réel

#### 4. Gestion des crashes (`move_crashes()`)
- Détecte automatiquement les fichiers crash (`crash-*`)
- Les déplace dans `./crashes/`
- Pour chaque crash trouvé :
  - Affiche un hexdump formaté avec `xxd`
  - Affiche les bytes en format C-style

### Support pour d'autres cibles

Le script est préparé pour fuzzer d'autres bibliothèques. Par exemple, pour fuzzer JPEGFuzz :

```python
# Décommenter ces lignes pour fuzzer JPEGFuzz :
# TARGET_BIN = "/rootfs/jpegfuzz" 
# TARGET_LIB = "/rootfs/system/lib64/libJpegFuzz.so"
```

## Exemple de sortie

```
[🔨] Sloth not found — running make...
=== 🚀 Launching Sloth Fuzzer ===
INFO: Running with entropic power schedule (0xFF, 100).
INFO: Seed: 2481397215
INFO: 10 files found in ./test
...
==3356== ERROR: libFuzzer: deadly signal
[+] Crash detected: crash-b6b38fae3408894aae30f3935999d4803cb47633

🧨 Crash hex dump (crash-b6b38fae3408894aae30f3935999d4803cb47633):

00000000: dead bede efca caca caca caca caca caca  ................
00000010: caca caca caca caca caca caca caca caca  ................
...

📦 Crash bytes (C-style):

0xDE, 0xAD, 0xBE, 0xDE, 0xEF, 0xCA, 0xCA, 0xCA, ...

==> Fuzzing completed in 4.52 seconds.
🗂 Crash files saved in: ./crashes/
```

## Fonctionnement de la bibliothèque vulnérable

La fonction `libQemuFuzzerTestOneInput` dans `fuzz.cpp` contient une vulnérabilité intentionnelle :

```cpp
if (Data[0] == 0xde) {
    if (Data[1] == 0xad) {
        if (Data[2] == 0xbe) {
            if (Data[4] == 0xef) {
                if (Data[55] == 0xca) {
                    char * ptr = (char*) 0x61616161;
                    ptr[0] = 0;  // Crash intentionnel
                }
            }
        }
    }
}
```

Le fuzzer cherche à découvrir la séquence magique qui déclenche le crash.

## Commandes utiles

Examiner le contenu d'un crash :
```bash
xxd ./crashes/crash-[hash]
```

Visualiser les fichiers de crash disponibles :
```bash
ls ./crashes/
```

Relancer le fuzzing avec un corpus existant :
```bash
python3 fuzz_runner.py
```

## Personnalisation

Vous pouvez modifier les paramètres dans `fuzz_runner.py` :

- Changer le nombre de cas de test : `NB_CASES`
- Modifier la taille maximale des inputs : `MAX_INPUT_SIZE`
- Utiliser une autre bibliothèque cible : modifier `TARGET_BIN` et `TARGET_LIB`

## Dépannage

- **Docker non démarré** : Démarrez Docker avant de lancer `./run.sh`
- **Compilation échoue** : Vérifiez que le chemin vers le rootfs est correct (`/rootfs/`)
- **Pas de crash trouvé** : Normal si la bibliothèque n'a pas de vulnérabilité ou si les inputs sont inadéquats
- **Erreur file not found** : Assurez-vous d'être dans le bon répertoire (`/sloth/src/`)
# Contrôle des comptes
version: 0.0.1

## Contraintes à appliquer pour le développement de l'application coco
Toutes les contraintes concernant les règles de codage et d'architecture sont résumées dans le document CH00_Development_Guideline.md (lui aussi situé dans ./doc/spec)

## Données primaires
Les données primaires (aussi appelées données d'entrée) pour le contrôle des compte fourni par le syndic, se présentent sous la forme d'un fichier pdf de plusieurs centaines de pages. Ce document qui sera appelé par la suite PES (Pdf d'Entrée Syndic) comporte principalement 3 types de documents:
- L'état des dépenses (abrégé EDD dans le reste des documents de spécification)
- des factures
- des rapports techniques.
- des demandes d'intervention établies par le syndic pour mandater des entreprise afin qu'elles interviennent.
- un document de répartition de l'eau établi par le syndic (appellé RES pour Repart Eau Syndic, dans le reste des spécifications)
- un document de compteur d'eau individuel établi par l'entreprise (RECI pour Repart Eau Compteurs Individuels dans le reste des spécifications) 


## Specifiations 
#### UReq1:
v0.1
status: specified
L'utilisateur doit pouvoir exécuter une ligne de commande sur laquelle il appellera l'outil "coco" puis il passera en paramètre un traitement à appliquer (une commande interne de l'outil coco), et le document PES. Les traitements à appliquer reçu en paramètre (ou commande interne de l'outil) seront spécifiées dans d'autres exigences (UReq).

#### UReq2
v0.1
status: specified
Un fichier caché ".coco_cfg" permet de configurer le comportement par défaut de l'outil coco afin de ne pas obliger l'utilisateur à spécifier trop de paramètres lorsqu'il invoque l'outil coco. Les principaux paramètres configurables sont:
- user.name 
- user.email
- out.folder
- account.years

Le fichier de configuration .coco_cfg pourra être stocké dans un répertoire .coco du répertoire utilisateur

#### UReq3
v0.1
status: specified
L'exercice comptable faisant l'objet du contrôle des comptes commence typiquement au cours d'une année calandaire, et se termine sur l'année calandaire suivante. Dans le fichier de configuration .coco_cfg , la chaine de caractère indiquant les années concernées par l'exercice comptable sur lequel porte le contrôle des comptes, est donné par le paramètre account.years et peut avoir comme valeur par exemple "2024-2025".
Si ce paramètre n'est pas disponible dans le fichier de configuration .coco_cfg ou que ce fichier de configuration n'est pas disponible, alors la valeur de account.years par défaut sera l'année courant lue dans l'heure système du PC exécutant l'outil coco, et l'année suivante. Si par exemple, l'outil coco est exécuté en 2026 et que l'utilisateur n'a pas définit le paramètre account.years, alors on considèrera que l'exercice comptable porte sur les années 2026 et 2027.

#### UReq4:
v0.1
status: specified
La commande interne split permet a l'utilisateur de séparer le document principal pdf afin de splitter le pdf PES en différentes parties:
- d'un coté le document EDD qui doit être contenu dans un nouveau pdf appelé EDD_<annee>.pdf
- le document RES de répartition de l'eau établi par SYNDIA
- le document RECI établi par OCEA
- d'un autre coté, une collection de document pdf, rangé dans un sous répertoire factures_a_controler sous le répertoire out.folder du fichier de configuration .coco_cfg s'il existe, sinon, sous le répertoire courant. Ce répertoire doit contenir un document pdf pour chacune des factures identifiées dans le PES. Le nom de chacun de ces documents facture pdf est composé des éléments suivant :
	- F suivi de l'année de fin de l'exercice comptable (par exemple, si account.years = "2024-2025" alors le nom du document facture commencera par F2025).
	- p suivi du numéro de page dans le document original PES dont est extrait le document facture
	- Le nom de l'entreprise qui a édité la facture
	- année de la facture
	- mois de la facture
	- jour de la facture
	- montant en euros TTC de la facture
	
	Toutes ces composantes du nom du fichier facture sont séparées par des caractère underscore ("_"). En résumén le nom d'un fichier facture se résume comme suit:
	- F<Annee>_p<numeroPagedansPES>_NomEntreprise_annee_mois_numerojour__MontantEnEuros (par exemple: F2025_p23_Quadiant_20_11_24__14.92).
- Tous les autres documents inclus au PES (rapport techniques etc...) seront rangé dans un répertoire nommé "\extra".
	
	
#### UReq5:
v0.1
status: specified
Le document PES contient fréquemment des factures en double, ou triple, voir plus, exemplaires. Les documents facture pdf qui en résulte sont identiques exepté qu'ils diffèrent par le numéro de page dans le document PES. Ces factures doublons doivent être rangées dans un répertoire nommé "\doublons". Ces documens factures seront conservé comme doublon a des fin de traçabilité, mais ne seront pas à prendre en compte pour le contrôle des comptes effectif.
	

#FAQ

## Vyro est-il un remplacement de FastAPI ?

Vyro cible Python DX avec un moteur d'exécution Rust. Évaluez en fonction de votre charge de travail, de vos objectifs de latence et de votre modèle opérationnel.

## Pourquoi la documentation mentionne-t-elle `python -m vyro` ?

`vyro` est la commande principale destinée aux utilisateurs finaux. `python -m vyro` est une solution de secours lorsque le shell PATH n'est pas encore configuré.

## Les utilisateurs doivent-ils exécuter les commandes `scripts.dev.*` ?

Non. Les utilisateurs finaux doivent utiliser `vyro ...`. Les scripts de développeur sont des outils de maintenance internes.

## Vyro prend-il en charge WebSocket ?

Oui, via des primitives de périphérie d'exécution et des gestionnaires WebSocket au niveau de la route.

## Puis-je exécuter sur Python 3.13 ?

Oui. Vyro cible Python 3.10-3.13.
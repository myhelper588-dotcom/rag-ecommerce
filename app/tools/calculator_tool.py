from langchain.tools import tool

@tool
def calculate(operation: str) -> str:
    """
    Effectue des calculs mathématiques et financiers.
    Utilise cet outil dès qu'une question implique :
    - Un calcul de marge, coût, prix, bénéfice
    - Un pourcentage, taux, ratio
    - Une multiplication, addition, soustraction
    - Une perte financière, ROI, rentabilité
    - Toute opération arithmétique
    Exemples : '45 * 89', '(89-45)/89*100', '30 * 89 * 0.85'
    """
    try:
        # Sécurisé — uniquement des opérations mathématiques
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in operation):
            return "❌ Opération non autorisée"
        result = eval(operation)
        return f"✅ Résultat : {result:.2f}"
    except Exception as e:
        return f"❌ Erreur de calcul : {str(e)}"
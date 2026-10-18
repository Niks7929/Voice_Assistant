from services.calculator_service import CalculatorService


class CalculatorTool:
    @staticmethod
    def calculate(expression: str):
        try:
            result = CalculatorService.evaluate(expression)
            return f"The result is: {result}"
        except Exception as exc:
            return f"I could not calculate that expression. Error: {exc}"

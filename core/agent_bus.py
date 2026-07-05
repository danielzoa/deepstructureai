from datetime import datetime


class AgentBus:
    def __init__(self, logger=None):
        self.logger = logger
        self.messages = []

    def send(self, sender, receiver, task, content):
        message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "receiver": receiver,
            "task": task,
            "content": content
        }

        self.messages.append(message)

        if self.logger:
            self.logger.log(
                "AgentBus message",
                f"{sender} -> {receiver} | {task}"
            )

        return message

    def history(self):
        if not self.messages:
            return "Nenhuma mensagem interna registrada."

        lines = []

        for i, msg in enumerate(self.messages, start=1):
            lines.append(
                f"{i}. [{msg['timestamp']}] "
                f"{msg['sender']} -> {msg['receiver']} | {msg['task']}"
            )

        return "\n".join(lines)